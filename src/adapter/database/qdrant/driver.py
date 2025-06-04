from qdrant_client import QdrantClient, AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, TextIndexParams
from qdrant_client.models import Filter, FieldCondition
from typing import Optional


class QdrantDriver:
    def __init__(self, host="localhost", port=6333):
        self.client = QdrantClient(host=host, port=port)
        self.client_async = AsyncQdrantClient(host=host, port=port)

    def create_collection(
        self,
        collection_name: str,
        size: int = 1536,
        distance: Distance = Distance.COSINE,
        payload_schema: dict = {},
    ):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=size, distance=distance),
        )

        if payload_schema:
            for field_name, schema in payload_schema.items():
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=TextIndexParams(
                        type=schema["type"],
                        tokenizer=schema["tokenizer"],
                        lowercase=schema["lowercase"]
                    )
                )

    async def insert_point(self, collection_name: str, point: dict):
        await self.client_async.upsert(collection_name=collection_name, points=[point])

    def insert_batch(
        self, collection_name: str, points: list[dict], batch_size: int = 100
    ):
        try:
            for i in range(0, len(points), batch_size):
                batch_points = points[i : i + batch_size]
                self.client.upsert(collection_name=collection_name, points=batch_points)
        except Exception as e:
            print(f"Erro ao inserir batch: {e}")

    from qdrant_client.models import Filter, FieldCondition, MatchValue

    async def hybrid_search(
        self, collection_name, query_vector, field=None, value=None, limit=10
    ):
        query_filter = None
        if field and value:
            query_filter = Filter(
                must=[FieldCondition(key=field, match={"text": value})]
            )

        print(f"Query filter: {query_filter}")

        results = await self.client_async.search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=limit,
        )
        return results
