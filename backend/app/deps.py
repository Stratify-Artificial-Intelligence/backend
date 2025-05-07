from datetime import datetime
from typing import Callable, Type

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_session
from app.domain import (
    Business as BusinessDomain,
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum
from app.repositories import (
    BaseRepository,
    BusinessRepository,
    ChatRepository,
    UserRepository,
)
from app.schemas import BusinessResearch, BusinessResearchParams, TokenData
from app.security import check_auth_token
from app.services.openai import (
    add_message_to_chat,
    add_message_to_chat_and_get_response,
    create_chat,
)
from app.services.perplexity import deep_research


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def _get_repo(db: AsyncSession = Depends(get_session)) -> BaseRepository:
        return repo_type(db)

    return _get_repo


async def get_current_user(
    token_data: TokenData = Depends(check_auth_token),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserDomain:
    user = await users_repo.get_by_username(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
    return user


async def get_current_active_user(
    current_user: UserDomain = Depends(get_current_user),
) -> UserDomain:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return current_user


async def get_business(
    business_id: int,
    user: UserDomain,
    business_repo: BusinessRepository,
    permission_func: Callable[[BusinessDomain, UserDomain], bool],
    load_hierarchy: bool = False,
) -> BusinessDomain | BusinessIdeaDomain | EstablishedBusinessDomain:
    business = (
        await business_repo.get_child(business_id=business_id)
        if load_hierarchy
        else await business_repo.get(business_id=business_id)
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Business not found',
        )
    if not permission_func(business, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have enough privileges.',
        )
    return business


# ToDo (pduran): Should this function be here?
async def add_store_message_and_get_store_response(
    chat: ChatDomain,
    message: ChatMessageDomain,
    chats_repo: ChatRepository,
) -> ChatMessageDomain | None:
    """Register message and get the AI response."""
    await chats_repo.add_message(message),
    response_content = await add_message_to_chat_and_get_response(
        chat_internal_id=chat.internal_id,
        content=message.content,
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


def deep_research_for_business(
    business: BusinessIdeaDomain | EstablishedBusinessDomain,
    params: BusinessResearchParams,
) -> BusinessResearch:
    """Perform deep research for a business."""
    research_context = business.get_information()
    research_instructions = _get_deep_search_instructions()
    return deep_research(
        prompt=f'{research_context} {research_instructions}',
        max_tokens=params.max_tokens,
    )


def _get_deep_search_instructions() -> str:
    return """
    Instrucciones para la investigación en profundidad:
    La respuesta debe estar estructurada en párrafos claros, optimizados y de lectura ágil, empleando economía de lenguaje (máxima cantidad de información con el mínimo número de palabras, sin sacrificar claridad o profundidad).
    La información debe ser estratégica, actualizada y específica para aportar el máximo valor posible al usuario.
    Debes desarrollar los siguientes apartados:

    1. Cuota de mercado
    - Incluir datos actuales y estimaciones de participación de mercado en el sector específico del usuario, contando sector directo e indirecto.
    - Indicar fuentes recientes y comparativas si existen.

    2. Crecimiento sectorial
    - Analizar el ritmo de crecimiento histórico y proyectado del sector.
    - Identificar las principales tendencias actuales y previsiones a corto, medio y largo plazo.

    3. Competencia
    - Identificar competidores clave (locales e internacionales si aplica).
    - Analizar su posicionamiento estratégico.
    - Evaluar fortalezas, debilidades y ventajas comparativas frente al usuario.

    4. Innovaciones y metodologías relevantes
    - Incluir casos de éxito aplicables al contexto del usuario.
    - Analizar metodologías innovadoras vigentes en el sector.
    - Evaluar cómo podrían adaptarse o implementarse para el usuario.

    5. Público objetivo
    - Análisis profundo del cliente ideal: quién es, qué necesita, cuáles son sus puntos de dolor, deseos y motivaciones.
    - Definir los hábitos de consumo y los canales de información y decisión más efectivos para alcanzarlo.

    6. Tendencias del mercado
    - Reportar cambios relevantes en el comportamiento del consumidor.
    - Incluir tecnologías emergentes que puedan impactar el sector del usuario.
    - Analizar los marcos regulatorios pertinentes y su posible evolución.

    7. Análisis del producto/servicio del usuario
    - Evaluar la propuesta de valor actual.
    - Identificar ventajas competitivas reales.
    - Detectar debilidades o áreas de mejora.
    - Analizar el ajuste (fit) del producto/servicio respecto al mercado objetivo.

    8. Barreras de entrada y salida del sector
    - Identificar los principales obstáculos estructurales que dificultan la entrada de nuevos competidores (regulación, capital, fidelización, etc.).
    - Evaluar también las barreras de salida y su impacto en la dinámica competitiva del sector.

    9. Cadena de valor del sector
    - Analizar cómo se genera y distribuye el valor desde proveedores hasta el cliente final.
    - Detectar oportunidades de innovación, eficiencia y mejora.
    - Identificar posibles puntos críticos o cuellos de botella.

    10. Canales de distribución y ventas
    - Analizar los canales más efectivos y usados actualmente para llegar al cliente objetivo.
    - Identificar tendencias emergentes en modelos de comercialización.
    - Evaluar ventajas, limitaciones y perspectivas de cada canal.

    11. Factores macroeconómicos y contexto geopolítico
    - Detectar variables externas que puedan impactar directamente o indirectamente al negocio (inflación, tipos de interés, comercio internacional, estabilidad política, riesgos país, etc.).
    - Analizar impacto potencial sobre la estrategia del usuario y construir posibles escenarios de riesgo.

    12. Sostenibilidad y responsabilidad social
    - Identificar las prácticas sostenibles relevantes para el sector.
    - Evaluar la percepción de mercado sobre criterios ESG (ambientales, sociales y de gobernanza).
    - Detectar oportunidades estratégicas en sostenibilidad, tanto reputacionales como regulatorias.

    13. Alianzas estratégicas y ecosistema de innovación
    - Explorar actores clave con los que colaborar: startups, universidades, centros de I+D, hubs de innovación, corporativos.
    - Detectar redes de innovación activas en el sector.
    - Evaluar el potencial de alianzas estratégicas para acelerar crecimiento, innovación o expansión internacional.

    14. Análisis de riesgos y gestión de crisis
    - Identificar los principales riesgos tecnológicos, operativos, financieros, reputacionales, regulatorios, etc.
    - Definir estrategias de mitigación y planes de contingencia adaptados al contexto del usuario.

    15. Ecosistema y oportunidades de apoyo
    - Mapear fondos de inversión, inversores activos en el nicho.
    - Identificar incubadoras, aceleradoras relevantes.
    - Detallar eventos del sector, pitch competitions, grants públicos disponibles y sus fechas límite.
    - Incluir actores influyentes: influencers, consultores, medios especializados y redes de apoyo.

    Notas adicionales:
    - La respuesta debe ser integral, relevante y específica, no genérica.
    - La respuesta debe estar desarrollada si o si en formato parrafo con distintos párrafos, evitando a toda costa esquemas por puntos y tablas.
    - Utilizar fuentes de información actualizadas y confiables siempre que sea posible.
    - Cada sección debe estar conectada con el contexto inicial para asegurar aplicabilidad directa al caso del usuario.
    - Evitar repeticiones innecesarias.
    """  # noqa E501
