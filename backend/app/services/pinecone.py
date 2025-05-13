from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone.models import ServerlessSpec

from app.settings import PineconeSettings, RAGSettings

pinecone_settings = PineconeSettings()
rag_settings = RAGSettings()

pc = Pinecone(
    api_key=pinecone_settings.API_KEY,
    environment=pinecone_settings.REGION,
)


if rag_settings.INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=rag_settings.INDEX_NAME,
        dimension=rag_settings.INDEX_DIMENSION,
        metric=rag_settings.INDEX_METRIC,
        spec=ServerlessSpec(
            cloud=pinecone_settings.CLOUD,
            region=pinecone_settings.REGION,
        ),
    )
index = pc.Index(rag_settings.INDEX_NAME)


def upload_vectors(
    namespace: str,
    vectors: list[tuple[str, list[float], dict[str, str]]],
) -> None:
    index.upsert(vectors=vectors, namespace=namespace)


def search_vectors(
    namespace: str,
    query_vector: list[float],
    top_k: int,
) -> list[str]:
    result = index.query(
        namespace=namespace,
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
    )
    return[match['metadata']['text'] for match in result.get('matches', [])]
