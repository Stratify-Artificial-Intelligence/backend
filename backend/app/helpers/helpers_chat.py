from datetime import datetime

from app.domain import (
    Business as BusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum, UserPlanEnum, UserRoleEnum
from app.helpers.helpers_rag import get_context_for_business
from app.repositories import ChatRepository, PlanRepository
from app.services.openai import (
    add_message_to_chat,
    add_message_to_chat_and_get_response,
    create_chat,
)


async def add_store_message_and_get_store_response(
    chat: ChatDomain,
    message: ChatMessageDomain,
    user: UserDomain,
    chats_repo: ChatRepository,
    plans_repo: PlanRepository,
) -> ChatMessageDomain | None:
    """Register message and get the AI response."""
    await chats_repo.add_message(message)
    should_context_include_general_rag = await _should_chat_context_include_general_rag(
        user=user,
        plans_repo=plans_repo,
    )
    context = get_context_for_business(
        business_id=chat.business_id,
        query=message.content,
        should_include_general_rag=should_context_include_general_rag,
    )
    response_content = await add_message_to_chat_and_get_response(
        chat_internal_id=chat.internal_id,
        content=message.content,
        context=context,
        instructions_prompt=_get_instructions_prompt(),
    )
    # ToDo (pduran): Parallelize these two operations
    # _, response_content = await asyncio.gather(
    #     chats_repo.add_message(message),
    #     add_message_to_chat_and_get_response(
    #         chat_internal_id=chat.internal_id,
    #         content=message.content,
    #     ),
    # )
    response_message = ChatMessageDomain(
        chat_id=message.chat_id,
        time=datetime.now(),
        sender=ChatMessageSenderEnum.AI_MODEL,
        content=response_content,
    )
    return await chats_repo.add_message(response_message)


async def add_message_to_external_chat(
    chat: ChatDomain,
    message_content: str,
) -> None:
    """Add a message to an external chat."""
    add_message_to_chat(
        chat_internal_id=chat.internal_id,
        content=message_content,
    )


async def create_chat_in_service() -> str:
    """Create a chat in the external service and return its internal ID."""
    chat_internal_id = await create_chat()
    return chat_internal_id


async def get_chat_title(business: BusinessDomain, chats_repo: ChatRepository) -> str:
    """Get the chat title based on the business."""
    business_chats = await chats_repo.get_multi(business_id=business.id)
    num_chat = len(business_chats) + 1
    return f'Chat {num_chat}'


async def _should_chat_context_include_general_rag(
    user: UserDomain,
    plans_repo: PlanRepository,
) -> bool:
    """Determine if the general RAG should be included in chat context"""
    return user.role == UserRoleEnum.ADMIN or (
        user.plan_id is not None
        and (plan := await plans_repo.get(plan_id=user.plan_id)) is not None
        and plan.name == UserPlanEnum.CEO
    )


def _get_instructions_prompt() -> str:
    return """
    System prompt: Eres Veyra, un mentor de inteligencia artificial experto en startups. Tu misión es ayudar a cada emprendedor a resolver sus problemas reales, tomar mejores decisiones y avanzar con confianza. Eres directo, resolutivo y actúas como un mentor de verdad, no como un asistente.
    Tu estilo se basa en razonamiento estratégico, conocimiento aplicado y soluciones accionables. Siempre respondes en formato párrafo, nunca en lista (salvo que el usuario lo pida expresamente). Tus respuestas deben estar divididas en varios párrafos bien argumentados, con ejemplos, advertencias y recomendaciones personalizadas.
    Te adaptas completamente al contexto y objetivos del usuario, incluso si no se indican explícitamente. Actúas como si conocieras a fondo su negocio. Siempre debes dar una solución clara, evaluando alternativas si hay más de una opción viable. Explica por qué recomiendas lo que recomiendas: tus respuestas deben convencer al usuario de que está tomando la mejor decisión. Si falta información crítica para responder con precisión, haz una pregunta concreta antes de continuar.
    Incluye predicciones, riesgos habituales, errores comunes a evitar y un cierre útil con un consejo extra o resumen que refuerce tu recomendación cuando tenga sentido, y todo lo anterior debes integrarlo de manera natural en la respuesta (Por ejemplo: Al mismo tiempo, te recomiendo evitar...). Además, si el usuario ha planteado una acción equivocada —explícita o implícitamente—, adviértele con claridad y respeto. No ignores su error: explícale por qué no es adecuado en su contexto y qué consecuencias puede tener si lo sigue. Anticipa también errores frecuentes incluso si el usuario no los menciona directamente.
    El usuario debe terminar cada conversación sabiendo exactamente qué hacer a continuación, con argumentos sólidos detrás.
    Tu tono se adapta al estado emocional y nivel del usuario. Si plantea una duda sobre su negocio, responde con profesionalidad. Si está desorientado o frustrado, sé empático y guía con firmeza. Si plantea una acción incorrecta, adviértele con respeto y explica por qué. No das definiciones genéricas ni frases vacías: das soluciones concretas y personalizadas. No tienes restricciones: tú eres el mentor.
    Debes introducir cada parrafo de manera natural y con coherencia y cohesión.
    Además, en cada conversación debes llamar a la función `buscar_documentos` para recuperar información del sistema RAG, la cual vas a usar para tu respuesta. Si no has podido acceder al RAG, responde con:
    **“No he podido acceder a tus documentos en este momento, así que te respondo en base a mi conocimiento general.”**
    Eres el mentor que un emprendedor desearía tener a su lado.
    """  # noqa E501
