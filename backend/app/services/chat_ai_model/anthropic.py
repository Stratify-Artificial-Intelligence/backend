import uuid
from typing import AsyncGenerator

from anthropic import Anthropic
from anthropic.types import ToolParam

from app.domain import (
    Business as BusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
)
from app.enums import ChatMessageSenderEnum
from app.services.chat_ai_model.base import ChatAIModelProvider
from app.settings import AnthropicSettings


settings = AnthropicSettings()


class ChatAIModelAnthropic(ChatAIModelProvider):
    """Anthropic chat model provider using explicit message history."""

    def __init__(self):
        self.client = Anthropic(api_key=settings.API_KEY)
        self.tools = [
            ToolParam(
                type='custom',
                name='get_internal_knowledge',
                description='Consulta la base de conocimiento empresarial propia.',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Consulta al RAG interno.',
                        }
                    },
                    'required': ['query'],
                },
            ),
            ToolParam(
                type='custom',
                name='get_market_research',
                description='Consulta a la investigación de mercado.',
                input_schema={
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'Consulta al RAG externo.',
                        }
                    },
                    'required': ['query'],
                },
            ),
        ]

    @staticmethod
    async def create_chat() -> str:
        return str(uuid.uuid4())

    async def add_message_to_chat_and_get_response(
        self,
        business: BusinessDomain,
        chat: ChatDomain,
        content: str,
        business_rag: str,
        general_rag: str,
    ) -> str:
        messages = [self._business_info_to_anthropic_message(business=business)]
        if chat.messages is not None:
            messages.extend(
                [
                    self._chat_message_domain_to_anthropic_message(msg)
                    for msg in chat.messages
                ]
            )

        # Add user message to history
        messages.append(
            {
                'role': ChatMessageSenderEnum.USER.value,
                'content': [{'type': 'text', 'text': content}],
            }
        )

        response = self.client.messages.create(
            model=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            messages=messages,
            system=self.get_instructions_prompt(),
            tools=self.tools,
        )

        return await self._process_response(
            messages=messages,
            instructions_prompt=self.get_instructions_prompt(),
            business_rag=business_rag,
            general_rag=general_rag,
            response=response,
        )

    async def add_message_to_chat_and_get_response_stream(
        self,
        business: BusinessDomain,
        chat: ChatDomain,
        content: str,
        business_rag: str,
        general_rag: str,
    ) -> AsyncGenerator[str, None]:
        """Streams Claude's response, handling tool_use blocks (RAG injection)."""

        messages = [self._business_info_to_anthropic_message(business=business)]
        if chat.messages:
            messages.extend(
                [self._chat_message_domain_to_anthropic_message(msg) for msg in
                 chat.messages]
            )
        messages.append(
            {
                'role': 'user',
                'content': [{'type': 'text', 'text': content}],
            }
        )

        system_prompt = self.get_instructions_prompt()

        async def stream_from(messages: list[dict]) -> AsyncGenerator[str, None]:
            with self.client.messages.stream(
                model=settings.MODEL_NAME,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                messages=messages,
                system=system_prompt,
                tools=self.tools,
            ) as stream:
                assistant_blocks = []
                tool_use_block = None

                for block in stream:
                    if block.type == 'text':
                        yield block.text
                        assistant_blocks.append(block)
                    elif block.type == 'tool_use':
                        tool_use_block = block
                        assistant_blocks.append(block)
                        # Pause stream to handle tool
                        break

            messages.append({'role': 'assistant', 'content': assistant_blocks})

            # If tool_use_block was received, inject tool result and resume
            if tool_use_block:
                tool_result = self._handle_tool_call(
                    tool_name=tool_use_block.name,
                    business_rag=business_rag,
                    general_rag=general_rag,
                )

                messages.append(
                    {
                        'role': 'user',
                        'content': [{
                            'type': 'tool_result',
                            'tool_use_id': tool_use_block.id,
                            'content': tool_result,
                        }],
                    }
                )

                # Recursively resume stream
                async for next_chunk in stream_from(messages):
                    yield next_chunk

        return stream_from(messages)

    @staticmethod
    def get_new_message_credit_cost(chat: ChatDomain) -> int:
        if chat.messages is None:
            raise ValueError(
                'Credit cost cannot be calculated for a chat without messages '
                'information.'
            )
        new_message_num = len(chat.messages) + 1
        if new_message_num == 1:
            return 2
        elif 2 <= new_message_num <= 6:
            return 3
        elif 7 <= new_message_num <= 9:
            return 4
        elif 10 <= new_message_num <= 14:
            return 5
        elif 15 <= new_message_num <= 18:
            return 6
        elif 19 <= new_message_num <= 20:
            return 7
        else:
            return 8

    async def _process_response(
        self,
        messages: list[dict],
        instructions_prompt: str,
        business_rag: str,
        general_rag: str,
        response,
    ) -> str:
        # Full response of the model
        full_response = ''

        # Assistant responses blocks
        assistant_blocks = []

        # There may be a block (at most 1) with tool_use
        tool_use_block = None

        for block in response.content:
            if block.type == 'text':
                full_response += block.text
            elif block.type == 'tool_use':
                tool_use_block = block
            assistant_blocks.append(block)

        messages.append(
            {
                'role': 'assistant',
                'content': assistant_blocks,
            }
        )

        # If tool_use exists, respond with tool_result
        if tool_use_block:
            tool_result = self._handle_tool_call(
                tool_name=tool_use_block.name,
                business_rag=business_rag,
                general_rag=general_rag,
            )

            messages.append(
                {
                    'role': ChatMessageSenderEnum.USER.value,
                    'content': [
                        {
                            'type': 'tool_result',
                            'tool_use_id': tool_use_block.id,
                            'content': tool_result,
                        }
                    ],
                }
            )

            resumed = self.client.messages.create(
                model=settings.MODEL_NAME,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                messages=messages,
                system=instructions_prompt,
                tools=self.tools,
            )

            return await self._process_response(
                messages=messages,
                instructions_prompt=instructions_prompt,
                business_rag=business_rag,
                general_rag=general_rag,
                response=resumed,
            )

        return full_response

    @staticmethod
    def _handle_tool_call(tool_name: str, business_rag: str, general_rag: str) -> str:
        if tool_name == 'get_internal_knowledge':
            return business_rag
        elif tool_name == 'get_market_research':
            return general_rag
        return '[Error: herramienta desconocida]'

    @staticmethod
    def _business_info_to_anthropic_message(
        business: BusinessDomain,
    ) -> dict:
        """Convert business info to an Anthropic message format."""
        return {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': business.get_information(),
                }
            ],
        }

    @staticmethod
    def _chat_message_domain_to_anthropic_message(
        chat_message: ChatMessageDomain,
    ) -> dict:
        """Convert a chat message domain to an Anthropic message format."""
        try:
            role = {
                ChatMessageSenderEnum.USER.value: 'user',
                ChatMessageSenderEnum.AI_MODEL.value: 'assistant',
            }[chat_message.sender.value]
        except KeyError:
            raise NotImplementedError(
                f'Message sender {chat_message.sender.value} not implemented.'
            )
        return {
            'role': role,
            'content': [{'type': 'text', 'text': chat_message.content}],
        }
