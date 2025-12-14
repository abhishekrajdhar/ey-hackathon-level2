from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.routers import health, sales, pipeline, inventory
from fastapi.middleware.cors import CORSMiddleware


setup_logging()
settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Agentic AI-style backend for B2B RFP response (Sales, Technical, Pricing Agents).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(sales.router, prefix=settings.api_v1_prefix)
app.include_router(pipeline.router, prefix=settings.api_v1_prefix)
app.include_router(inventory.router, prefix=settings.api_v1_prefix)
