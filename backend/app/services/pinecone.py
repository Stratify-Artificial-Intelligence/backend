from pinecone.grpc import PineconeGRPC as Pinecone

from app.settings import PineconeSettings, RAGSettings

pinecone_settings = PineconeSettings()
rag_settings = RAGSettings()

pc = Pinecone(
    api_key=pinecone_settings.API_KEY,
    environment=pinecone_settings.ENVIRONMENT,
)


if rag_settings.INDEX_NAME not in pc.list_indexes():
    pc.create_index(
        name=rag_settings.INDEX_NAME,
        dimension=rag_settings.INDEX_DIMENSION,
        metric=rag_settings.INDEX_METRIC,
    )


def upload_vectors(
    namespace: str,
    vectors: list[tuple[str, list[float], dict[str, str]]],
) -> None:

