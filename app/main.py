from fastapi import FastAPI
from app.routers import posts
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API")

app.include_router(posts.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
