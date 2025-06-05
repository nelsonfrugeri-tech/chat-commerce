import json
from pydantic import BaseModel
from src.domain.product import Payload
from src.adapter.service.openai.client import OpenAIClient
from src.adapter.database.qdrant.driver import QdrantDriver

openai_client = OpenAIClient()
qdrant_driver = QdrantDriver()


def get_nested_fields(model: BaseModel, prefix=""):
    fields = []
    for field_name, field in model.model_fields.items():
        field_type = field.annotation
        if hasattr(field_type, "model_fields"):  # Verifica se é um modelo aninhado
            fields.extend(
                get_nested_fields(field_type, prefix=f"{prefix}{field_name}.")
            )
        else:
            fields.append(f"{prefix}{field_name}")
    return fields


async def chat(query_text: str, field: str = None, value: str = None, limit: int = 10):
    entity_recognition_prompt = [
        {
            "role": "system",
            "content": (
                "You are an assistant that extracts entities and their corresponding values from the user's query. "
                f"Available fields in the products collection are: {', '.join(get_nested_fields(Payload))}"
                "Prioritize the 'product_name', 'product_details' 'description' and 'search_keyword' fields."
                "Return a JSON object with 'field' and 'value' keys if any entity is found, otherwise return an empty object."
            ),
        },
        {"role": "user", "content": query_text},
    ]
    query_filter_response = await openai_client.chat_with_json_response(
        messages=entity_recognition_prompt,
        model="gpt-4.1-nano",
    )
    query_filter = (
        query_filter_response if isinstance(query_filter_response, dict) else {}
    )

    print(f"Query filter: {query_filter}")

    filter_field = query_filter.get("field", field)
    filter_value = query_filter.get("value", value)

    query_vector = await openai_client.embed(query=query_text)
    search_results = await qdrant_driver.hybrid_search(
        collection_name="products_v1",
        query_vector=query_vector,
        field=filter_field,
        value=filter_value,
        limit=limit,
    )

    print(f"Search results: {search_results}")

    if len(search_results) > 0:
        context = [result.payload for result in search_results]

        rerank_messages = [
            {
                "role": "system",
                "content": (
                    "You are an e-commerce assistant. Your task is to re-rank and validate each product individually based on relevance and factual accuracy "
                    "related to the user's query. If any product is not related or does not make sense, remove it completely from the list. "
                    "Return a JSON object containing a 'products' list reordered and validated. "
                    f"Original products:\n{json.dumps(context, ensure_ascii=False)}"
                ),
            },
            {"role": "user", "content": query_text},
        ]

        validated_products_response = await openai_client.chat_with_json_response(
            messages=rerank_messages,
            model="gpt-4.1-nano",
        )
        validated_products = validated_products_response.get("products", [])

        print(f"Validated products: {validated_products}")

        streaming_context = "\n".join(
            [json.dumps(prod, ensure_ascii=False) for prod in validated_products]
        )

        chat_messages = [
            {
                "role": "system",
                "content": (
                    "You are an e-commerce assistant. Use the provided context, which includes only validated and reordered products, "
                    "to answer the user's query in the most clear and useful way possible. "
                    "If the user's query is not related to the products, return 'I'm sorry, I can't help with that.' "
                    f"Context of the products:\n{streaming_context}"
                ),
            },
            {"role": "user", "content": query_text},
        ]

        async for chunk in openai_client.stream_chat_completion(messages=chat_messages):
            yield chunk
    else:
        yield "I'm sorry, I can't help with that."
