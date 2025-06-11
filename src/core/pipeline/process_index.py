import asyncio
import csv
from pathlib import Path
from src.domain.product import Product, Payload, Merchant
from src.adapter.database.qdrant.driver import QdrantDriver

DATASET_PATH = Path(__file__).resolve().parents[2] / "../datasource/dataset.csv"
COLLECTION_NAME = "products_v2"
EMBEDDING_MODEL = "text-embedding-3-small"

qdrant = QdrantDriver(collection_name=COLLECTION_NAME)
qdrant.create_collection()


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
                    without_discount_price=await safe_float(
                        row.get("withoutDiscountPrice")
                    ),
                )

                product = Product(payload=payload)

                await qdrant.upsert_point(
                    point_id=idx,
                    text=payload.product_details
                    or payload.description
                    or payload.product_name
                    or "",
                    payload=product.payload.model_dump(),
                )

                print(f"[INFO] Produto indexado com sucesso: {product.id}")

            except Exception as e:
                print(f"[ERRO] Falha ao processar linha {idx}: {e}")


if __name__ == "__main__":
    asyncio.run(process_and_index())
