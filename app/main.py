from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from app.db import engine, seed_db
from app.views import router as views_router
from app.api.blog import router as blog_router
from app.api.projects import router as projects_router
from app.api.auth import router as auth_router
from app.api.comments import router as comments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Seed database
    await seed_db()
    
    yield

app = FastAPI(title="Portfolio Jinja2+HTMX", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include views router
app.include_router(views_router)

# Include API routers
app.include_router(blog_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(comments_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
