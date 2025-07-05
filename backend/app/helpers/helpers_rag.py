from app.domain import (
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
)
from app.schemas import BusinessResearch, BusinessResearchParams
from app.services import ServicesFactory
from app.services.perplexity import deep_research
from app.services.pinecone import search_vectors, upload_vectors

from tiktoken import encoding_for_model

from app.settings import GeneralRAGSettings, OpenAIEmbeddingSettings, RAGSettings

open_ai_embedding_settings = OpenAIEmbeddingSettings()
rag_settings = RAGSettings()
general_rag_settings = GeneralRAGSettings()


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


def chunk_and_upload_text_for_business(text: str, business_id: int) -> None:
    _chunk_and_upload_text(
        text=text,
        settings=rag_settings,
        namespace=rag_settings.NAMESPACE_ID.format(business_id=business_id),
    )


def chunk_and_upload_text_for_general(text: str) -> None:
    _chunk_and_upload_text(
        text=text,
        settings=general_rag_settings,
        namespace=general_rag_settings.NAMESPACE_ID,
    )


def _chunk_and_upload_text(text: str, settings: RAGSettings, namespace: str) -> None:
    chunks = chunk_text(
        text=text,
        max_tokens=settings.MAX_TOKENS,
        overlap=settings.OVERLAP,
    )
    vectors_to_upsert: list[tuple[str, list[float], dict[str, str]]] = []
    for chunk_index, chunk in enumerate(chunks):
        vector_id = settings.VECTOR_ID.format(
            doc_index=0,
            chunk_index=chunk_index,
        )
        vector = embed_text(text=chunk)
        metadata = {'text': chunk}
        vectors_to_upsert.append((vector_id, vector, metadata))
    upload_vectors(
        index_name=settings.INDEX_NAME,
        namespace=namespace,
        vectors=vectors_to_upsert,
    )


def chunk_text(text: str, max_tokens: int, overlap: int) -> list[str]:
    """Chunk text into smaller fragments of max_tokens size with overlap."""
    tokenizer = encoding_for_model(model_name=open_ai_embedding_settings.MODEL_NAME)
    tokens = tokenizer.encode(text)
    chunks = []
    if len(tokens) <= max_tokens:
        chunks.append(text)
    else:
        step = max_tokens - overlap
        for i in range(0, len(tokens), step):
            segment = tokens[i : i + max_tokens]
            if not segment:
                break
            chunked_text = tokenizer.decode(segment)
            chunks.append(chunked_text)
            if i + max_tokens >= len(tokens):
                break
    return chunks


def embed_text(text: str) -> list[float]:
    """Embed text."""
    embedding_provider = ServicesFactory().get_embedding_provider()
    return embedding_provider.create_embedding(text=text)


def get_context_for_business(
    business_id: int,
    query: str,
    should_include_general_rag: bool = False,
) -> str:
    """Get context for a business based on the query."""
    context_vectors = search_vectors_for_business(
        business_id=business_id,
        query=query,
    )
    context_str = '\n'.join(context_vectors)
    general_context_str = ''
    if should_include_general_rag:
        general_context_vectors = search_vectors_for_general(query=query)
        general_context_str = '\n'.join(general_context_vectors)

    return (
        f'Información recuperada del sistema RAG:\n\n {context_str}\n\n '
        f'{general_context_str}\n\n Instrucción: Con base en la información anterior '
        '(solo si es relevante para la respuesta) y tu propio razonamiento, responde a '
        'la pregunta.'
    )


def search_vectors_for_business(business_id: int, query: str) -> list[str]:
    """Search vectors in Pinecone."""
    query_vector = embed_text(query)
    return search_vectors(
        index_name=rag_settings.INDEX_NAME,
        namespace=rag_settings.NAMESPACE_ID.format(business_id=business_id),
        query_vector=query_vector,
        top_k=rag_settings.TOP_K,
    )


def search_vectors_for_general(query: str) -> list[str]:
    """Search vectors in Pinecone for general research."""
    query_vector = embed_text(query)
    return search_vectors(
        index_name=general_rag_settings.INDEX_NAME,
        namespace=general_rag_settings.NAMESPACE_ID,
        query_vector=query_vector,
        top_k=general_rag_settings.TOP_K,
    )


def _get_deep_search_instructions() -> str:
    return """
    System prompt:
    Eres un investigador estratégico experto en negocios tecnológicos. Tu tarea es escribir informes extensos (mínimo 10.000 palabras) y bien estructurados, con profundidad analítica, secciones bien diferenciadas por títulos claros, fuentes numeradas y un tono profesional. Redactas como un analista senior de una firma de consultoría como McKinsey o BCG. Tus informes deben ser ricos en contenido, evitar generalidades y aportar conclusiones aplicables. Cada sección debe estar titulada y explicada en formato narrativo extenso. No uses listas ni esquemas. La redacción debe fluir en párrafos completos bajo cada título, y debe construirse como un documento de análisis serio, riguroso y útil para tomadores de decisiones. Dado que la extensión es elevada, debes aprovecharla para introducir la mayor cantidad posible de información útil, cifras, datos de mercado, actores clave, tendencias y riesgos relevantes. La investigación debe estar en Español.
    
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
