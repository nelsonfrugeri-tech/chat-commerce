import uvicorn
from fastapi import FastAPI
from src.core.api.router import router_handler


def api():
    app = FastAPI(
        title="chat-commerce",
        description="chat-commerce API",
        version="0.1.0",
        contact={
            "name": "nelsonfrugeri.tech",
            "email": "nelsonfrugeri.tech@gmail.com",
        },
    )

    app.include_router(router_handler())

    return app


if __name__ == "__main__":
    uvicorn.run(api, factory=True, host="0.0.0.0", port=8000)
