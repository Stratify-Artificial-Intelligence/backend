import openai
import time

from openai.types.beta.threads import TextContentBlock

from app.enums import ChatMessageSenderEnum
from app.settings import OpenAISettings


settings = OpenAISettings()
openai.api_key = settings.API_KEY


async def add_message_to_chat_and_get_response(chat_internal_id: str, content: str) -> str:
    """Add a message to a chat and return the response of the AI model."""
    message_creation_run_id = _add_message(
        chat_internal_id=chat_internal_id,
        content=content,
    )
    _wait_message_response(
        chat_internal_id=chat_internal_id,
        run_id=message_creation_run_id,
    )
    message_response = _get_last_message_in_thread(chat_internal_id=chat_internal_id)
    return message_response


async def create_chat() -> str:
    """Create a chat and return its internal ID."""
    thread = openai.beta.threads.create()
    return thread.id


def _add_message(chat_internal_id: str, content: str) -> str:
    """Add a message to a thread and return run id."""
    openai.beta.threads.messages.create(
        thread_id=chat_internal_id,
        role=ChatMessageSenderEnum.USER.value,
        content=content,
    )
    run = openai.beta.threads.runs.create(
        thread_id=chat_internal_id,
        assistant_id=OpenAISettings.ASSISTANT_ID,
    )
    return run.id


def _wait_message_response(chat_internal_id: str, run_id: str) -> str:
    """Loop until message has been responded, and return run status."""
    while True:
        run = openai.beta.threads.runs.retrieve(
            thread_id=chat_internal_id,
            run_id=run_id,
        )
        # ToDo (pduran): Can be somehow use RunStatus literal instead of a string?
        #  See: openai/types/beta/threads/run_status.py
        if run.status in ['completed', 'failed']:
            return run.status
        time.sleep(1)


def _get_last_message_in_thread(chat_internal_id: str) -> str:
    """Get content of the last message in a thread."""
    messages = openai.beta.threads.messages.list(
        thread_id=chat_internal_id,
        order='desc',
        limit=1,
    )
    if messages in None or len(messages) != 1:
        raise ValueError('Invalid retrieved last messages.')
    last_message = messages[0]
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
