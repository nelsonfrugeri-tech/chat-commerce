from qdrant_client import QdrantClient, AsyncQdrantClient, models
from qdrant_client.models import Distance, VectorParams, TextIndexParams, MatchText
from qdrant_client.models import Filter, FieldCondition
from tqdm import tqdm

from src.adapter.service.openai.client import OpenAIClient


class QdrantDriver:
    def __init__(self, collection_name: str, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.client_async = AsyncQdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.dense_model_name = "text-embedding-3-small"
        self.sparse_model_name = "prithivida/Splade_PP_en_v1"
        self.openai_client = OpenAIClient()

    def create_collection(
        self,
        size: int = 1536,
        distance: Distance = Distance.COSINE,
    ):
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=size,
                    distance=models.Distance.COSINE,
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        )

    async def upsert_point(self, point_id: int, text: str, payload: dict):
        dense_vector = await self.openai_client.embed(text=text)

        if dense_vector is None:
            print(f"Não foi possível criar o embedding para o ponto {point_id}")
            return

        await self.client_async.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector={
                        "dense": dense_vector,
                        "sparse": models.Document(
                            text=text, model=self.sparse_model_name
                        ),
                    },
                    payload=payload,
                )
            ],
        )

    def insert_batch(self, points: list[dict], batch_size: int = 100):
        try:
            for i in range(0, len(points), batch_size):
                batch_points = points[i : i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name, points=batch_points
                )
        except Exception as e:
            print(f"Erro ao inserir batch: {e}")

    async def hybrid_search(self, text: str, field: str, value: str, limit=10):
        query_filter = None
        if field and value:
            query_filter = Filter(
                must=[FieldCondition(key=field, match=MatchText(text=value))]
            )
        
        query_vector = await self.openai_client.embed(text=text)

        search_result = await self.client_async.query_points(
            collection_name=self.collection_name,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            prefetch=[
                models.Prefetch(
                    query=query_vector,
                    using="dense",
                ),
                models.Prefetch(
                    query=models.Document(text=text, model=self.sparse_model_name),
                    using="sparse",
                ),
            ],
            query_filter=query_filter,
            limit=limit,
        )

        return search_result.points
