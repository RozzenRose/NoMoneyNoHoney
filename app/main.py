from fastapi import FastAPI, Depends, Response
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.incomes import router as incomes_router
from app.routers.purchases import router as purchases_router
from app.routers.reports import router as reports_router
from app.database.db_depends import get_db
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging


# ---------- Настройка логирования ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("NMNH")  # свой логгер
# logging.getLogger("uvicorn.access").setLevel(logging.INFO)


app = FastAPI()


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency",
    ["path"]
)


@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)

    duration = time.time() - start

    REQUEST_COUNT.labels(
        request.method,
        request.url.path,
        response.status_code
    ).inc()

    REQUEST_LATENCY.labels(request.url.path).observe(duration)
    return response


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/health")
async def work_check(db: Annotated[AsyncSession, Depends(get_db)]):
    return {"status": "ok",
            "db": f"{'ok' if db.is_alive() else 'dead'}"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(incomes_router)
app.include_router(purchases_router)
app.include_router(reports_router)