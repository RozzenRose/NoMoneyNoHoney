from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

app.include_router(auth_router)
app.include_router(categories_router)