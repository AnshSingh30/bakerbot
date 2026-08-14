from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .models import init_db
from .routers import business, chat, orders

app = FastAPI(title="BakerBot")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(business.router)
app.include_router(chat.router)
app.include_router(orders.router)
init_db()


@app.get("/health")
def health():
    return {"ok": True}
