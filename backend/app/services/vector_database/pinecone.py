from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone.models import ServerlessSpec

from app.services.vector_database.base import VectorDatabaseProvider
from app.settings import GeneralRAGSettings, PineconeSettings, RAGSettings


pinecone_settings = PineconeSettings()
rag_settings = RAGSettings()
general_rag_settings = GeneralRAGSettings()


class VectorDatabasePinecone(VectorDatabaseProvider):
    """Implementation of VectorDatabaseProvider using Pinecone."""

    def __init__(self):
        """Initialize Pinecone vector database connection."""
        super().__init__()
        self.pc = Pinecone(
            api_key=pinecone_settings.API_KEY,
            environment=pinecone_settings.REGION,
        )
        if rag_settings.INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=rag_settings.INDEX_NAME,
                dimension=rag_settings.INDEX_DIMENSION,
                metric=rag_settings.INDEX_METRIC,
                spec=ServerlessSpec(
                    cloud=pinecone_settings.CLOUD,
                    region=pinecone_settings.REGION,
                ),
            )
        if general_rag_settings.INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=general_rag_settings.INDEX_NAME,
                dimension=general_rag_settings.INDEX_DIMENSION,
                metric=general_rag_settings.INDEX_METRIC,
                spec=ServerlessSpec(
                    cloud=pinecone_settings.CLOUD,
                    region=pinecone_settings.REGION,
                ),
            )

    def upload_vectors(
        self,
        index_name: str,
        namespace: str,
        vectors: list[tuple[str, list[float], dict[str, str]]],
    ) -> None:
        index = self.pc.Index(index_name)

        # Delete the index if it exists and create a new one. This way, every time
        # we upload vectors, we ensure that the index is clean and contains only the
        # latest vectors.
        if namespace in index.describe_index_stats().namespaces:
            index.delete(delete_all=True, namespace=namespace)

        # Store the vectors in batches.
        # Note: Pinecone has a gRPC message size limit of
        # PineconeSettings.MESSAGE_LIMIT_MB MB. Thus, the upload of vectors is done in
        # batches to avoid exceeding this limit.
        batch_size = self._compute_safe_batch_size()
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i : i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)

    def search_vectors(
        self,
        index_name: str,
        namespace: str,
        query_vector: list[float],
        top_k: int,
    ) -> list[str]:
        index = self.pc.Index(index_name)
        result = index.query(
            namespace=namespace,
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
        )
        return [match['metadata']['text'] for match in result.get('matches', [])]

    def _compute_safe_batch_size(self) -> int:
        """Estimate a safe batch size for Pinecone upsert to avoid gRPC limit."""
        # Estimate the size of a single vector. This function can be used to upload
        # vectors for both RAG and General RAG settings, so the maximum size is used
        # to be safe.
        vector_size = max(
            self._vector_size(rag_settings),
            self._vector_size(general_rag_settings),
        )
        # Use 90% of the limit to be safe.
        safe_batch = int((pinecone_settings.MESSAGE_LIMIT_BYTES * 0.9) / vector_size)
        return max(1, safe_batch)

    @staticmethod
    def _vector_size(settings: RAGSettings) -> int:
        """Calculate the size of a single vector in bytes."""
        # 4 bytes per float32
        vector_bytes = settings.INDEX_DIMENSION * 4
        # Estimate metadata size by sampling a vector's metadata. Assuming 4 chars per
        # token (aprox), UTF-8 encoding (1 byte per char).
        metadata_bytes = settings.MAX_TOKENS * 4
        return vector_bytes + metadata_bytes
