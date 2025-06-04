from fastapi import APIRouter
from src.core.api.endpoint import endpoint


def router_handler():
    router = APIRouter()
    prefix = "/chat-commerce"

    router.include_router(
        endpoint,
        prefix=prefix,
        tags=["health", "chat"],
    )

    return router
