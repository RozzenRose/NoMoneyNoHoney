from fastapi import FastAPI, Request, Response
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.incomes import router as incomes_router
from app.routers.purchases import router as purchases_router
from app.routers.reports import router as reports_router
from app.rabbitmq import RabbitMQConnectionManager
import time
import logging


# ---------- Настройка логирования ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("NMNH")  # свой логгер
# logging.getLogger("uvicorn.access").setLevel(logging.INFO)

app = FastAPI()

'''
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # ---- Читаем тело запроса (в памяти) ----
    try:
        body_bytes = await request.body()
    except Exception as e:
        body_bytes = b""
        logger.exception("Cannot read request body")

    # Сообщение о запросе
    logger.info(f"Incoming -> {request.method} {request.url.path} Body={body_bytes[:100]!r}")

    # Восстанавливаем receive
    async def receive():
        return {"type": "http.request", "body": body_bytes}

    request = Request(request.scope, receive)

    # ---- Выполняем обработку и замер времени ----
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000

    # ---- Читаем тело ответа (безопасно) ----
    resp_body = b""
    try:
        # response.body_iterator — асинхронный итератор чанков
        async for chunk in response.body_iterator:
            resp_body += chunk
    except Exception:
        # Некоторые response объекты могут вести себя иначе; на отладке логируем исключение
        logger.exception("Failed to read response body via body_iterator")
        # В этом случае попробуем безопасно получить content, если оно есть
        try:
            resp_body = response.body  # может быть bytes
            if resp_body is None:
                resp_body = b""
        except Exception:
            resp_body = b""

    logger.info(
        f"Outgoing <- status={response.status_code} time={duration_ms:.2f}ms "
        f"ResponseBody={resp_body[:200]!r}"
    )

    # ---- Возвращаем новый Response с тем же содержимым, чтобы клиент получил его ----
    headers = dict(response.headers)
    # Удаляем старый content-length, чтобы он автоматически пересчитался
    headers.pop("content-length", None)

    return Response(
        content=resp_body,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type
    )
'''


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(incomes_router)
app.include_router(purchases_router)
app.include_router(reports_router)