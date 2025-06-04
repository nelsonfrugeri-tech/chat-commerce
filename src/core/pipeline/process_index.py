import asyncio
import csv
from pathlib import Path
from src.domain.product import Product, Payload, Merchant, Vector
from src.adapter.service.openai.client import OpenAIClient
from src.adapter.database.qdrant.driver import QdrantDriver

DATASET_PATH = Path(__file__).resolve().parents[2] / "../datasource/dataset.csv"
COLLECTION_NAME = "products_v1"
EMBEDDING_MODEL = "text-embedding-3-small"

openai_client = OpenAIClient()
qdrant = QdrantDriver()
qdrant.create_collection(
    collection_name=COLLECTION_NAME,        
    payload_schema={
        "product_name": {"type": "text", "tokenizer": "prefix", "lowercase": True},
        "product_details": {"type": "text", "tokenizer": "prefix", "lowercase": True},
        "description": {"type": "text", "tokenizer": "prefix", "lowercase": True},
        "search_keyword": {"type": "text", "tokenizer": "prefix", "lowercase": True},
    }
)


async def safe_float(value):
    try:
        return float(value.replace("$", "").replace(",", "").strip())
    except (ValueError, AttributeError):
        return None


async def safe_int(value):
    try:
        return int(value.replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0


async def process_and_index():
    with open(DATASET_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            print(f"[INFO] Processando linha {idx}")

            try:
                payload = Payload(
                    description=row.get("description") or None,
                    merchant=Merchant(
                        name=row.get("merchantName").strip(),
                        link=row.get("merchantLink").strip(),
                    ),
                    price=await safe_float(row.get("price")),
                    product_details=row.get("productDetails") or None,
                    product_link=row.get("productLink").strip(),
                    product_name=row.get("productName").strip(),
                    reviews_count=await safe_int(row.get("reviewsCount")),
                    reviews_score=await safe_float(row.get("reviewsScore")) or 0.0,
                    search_keyword=row.get("searchKeyword") or None,
                    without_discount_price=await safe_float(row.get("withoutDiscountPrice")),
                )

                if payload.product_details:
                    vector =Vector(
                        product_details_vector=await openai_client.embed(payload.product_details)
                    )
                elif payload.description:
                    vector =Vector(
                        product_details_vector=await openai_client.embed(payload.description)
                    )
                else:
                    vector =Vector(
                        product_details_vector=await openai_client.embed(payload.product_name)
                    )

                product = Product(payload=payload, vector=vector)

                await qdrant.insert_point(
                    collection_name=COLLECTION_NAME,
                    point={
                        "id": str(product.id),
                        "vector": vector.product_details_vector,  # Você pode usar um vetor específico aqui
                        "payload": product.payload.model_dump(),
                    },
                )

                print(f"[INFO] Produto indexado com sucesso: {product.id}")

            except Exception as e:
                print(f"[ERRO] Falha ao processar linha {idx}: {e}")


if __name__ == "__main__":
    asyncio.run(process_and_index())
