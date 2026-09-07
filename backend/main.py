from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from api.chat_history import router as chat_history_router
from api.forecast_history import router as forecast_history_router
from api.users import router as users_router
from database.session import engine
from api.auth import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="AI Farming Agent", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chat_history_router)
app.include_router(forecast_history_router)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return "Hello AI Farmer"


@app.post("/chat")
def chat() -> dict[str, str]:
    return {"message": "Hello Farmer"}
