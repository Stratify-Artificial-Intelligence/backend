import openai
import time

from openai.types.beta.threads import TextContentBlock
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from app.enums import ChatMessageSenderEnum
from app.services.chat_ai_model.base import ChatAIModelProvider
from app.settings import OpenAISettings


settings = OpenAISettings()
openai.api_key = settings.API_KEY


class ChatAIModelOpenAI(ChatAIModelProvider):
    async def add_message_to_chat_and_get_response(
        self,
        chat_internal_id: str,
        content: str,
        context: str,
        instructions_prompt: str | None = None,
    ) -> str:
        message_creation_run_id = self.add_message_to_chat(
            chat_internal_id=chat_internal_id,
            content=content,
            instructions_prompt=instructions_prompt,
        )
        self._add_context_to_message(
            chat_internal_id=chat_internal_id,
            run_id=message_creation_run_id,
            context=context,
        )
        self._wait_message_for_status(
            chat_internal_id=chat_internal_id,
            run_id=message_creation_run_id,
            status_list=['completed', 'failed'],
        )
        message_response = self._get_last_message_in_thread(
            chat_internal_id=chat_internal_id,
        )
        return message_response


    @staticmethod
    async def create_chat() -> str:
        thread = openai.beta.threads.create()
        return thread.id


    @staticmethod
    def add_message_to_chat(
        chat_internal_id: str,
        content: str,
        instructions_prompt: str | None = None,
    ) -> str:
        if instructions_prompt is not None:
            content += instructions_prompt
        openai.beta.threads.messages.create(
            thread_id=chat_internal_id,
            role=ChatMessageSenderEnum.USER.value,
            content=content,
        )
        run = openai.beta.threads.runs.create(
            thread_id=chat_internal_id,
            assistant_id=settings.ASSISTANT_ID,
        )
        return run.id


    def _add_context_to_message(
        self,
        chat_internal_id: str,
        run_id: str,
        context: str,
    ) -> None:
        """Add context to the message."""
        status = self._wait_message_for_status(
            chat_internal_id=chat_internal_id,
            run_id=run_id,
            status_list=['completed', 'failed', 'requires_action'],
        )
        if status == 'requires_action':
            run = openai.beta.threads.runs.retrieve(
                thread_id=chat_internal_id,
                run_id=run_id,
            )
            if run.required_action is None:
                return
            call = run.required_action.submit_tool_outputs.tool_calls[0]
            if call.function.name != 'buscar_documentos':
                raise NotImplementedError(
                    f'Function name {call.function.name} not implemented yet. Only '
                    '`buscar_documentos` function is implemented.'
                )
            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=chat_internal_id,
                run_id=run_id,
                tool_outputs=[ToolOutput(tool_call_id=call.id, output=context)],
            )


    @staticmethod
    def _wait_message_for_status(
        chat_internal_id: str,
        run_id: str,
        status_list: list[str],
    ) -> str:
        """Loop until message has been responded, and return run status."""
        while True:
            run = openai.beta.threads.runs.retrieve(
                thread_id=chat_internal_id,
                run_id=run_id,
            )
            # ToDo (pduran): Can we somehow use RunStatus literal instead of a string?
            #  See: openai/types/beta/threads/run_status.py
            if run.status in status_list:
                return run.status
            time.sleep(1)


    @staticmethod
    def _get_last_message_in_thread(chat_internal_id: str) -> str:
        """Get content of the last message in a thread."""
        messages = openai.beta.threads.messages.list(
            thread_id=chat_internal_id,
            order='desc',
            limit=1,
        )
        if messages.data is None or len(messages.data) != 1:
            raise ValueError('Invalid retrieved last messages.')
        last_message = messages.data[0]
        if len(last_message.content) != 1:
            raise NotImplementedError(
                'Message content with not exactly one block is not implemented yet.'
            )
        content_block = last_message.content[0]
        if type(content_block) is not TextContentBlock:
            raise NotImplementedError(
                'Message content different from text is not implemented yet.'
            )
        return content_block.text.value
