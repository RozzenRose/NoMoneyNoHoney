from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.incomes import router as incomes_router
from app.routers.purchases import router as purchases_router
from app.routers.reports import router as reports_router
from app.rabbitmq import RabbitMQConnectionManager


app = FastAPI()

'''
@app.on_event("startup")
async def startup_event():
    await RabbitMQConnectionManager.get_connection()


@app.on_event("shutdown")
async def shutdown_event():
    await RabbitMQConnectionManager.close_connection()
'''

@app.get("/")
async def root():
    return {"message": "Hello, world!"}


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(incomes_router)
app.include_router(purchases_router)
app.include_router(reports_router)