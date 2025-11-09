from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth as auth_router, bulk_import, scoring_routes
from app.core.logger import logger
import logging   # <-- built-in Python logging
from fastapi.middleware.cors import CORSMiddleware
from app.scoring.router import router as scoring_router




app = FastAPI(title="FastAPI User Auth Service")

# List of origins that are allowed to make requests
# For development, you can allow all with "*" or be specific
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",  # Common for VS Code Live Server
    "null", # Allows 'file://' origins (for opening index.html directly)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include auth routes
app.include_router(auth_router.router)
# app.include_router(admin_jobs.router)
# app.include_router(processor.router)
# app.include_router(importer.router)
# # app.include_router(jobs.router)
# app.include_router(occupation_router.router)
# app.include_router(skill_router.router)
# app.include_router(skillgroup_router.router)
# app.include_router(skill_hierarchy_router.router)
# app.include_router(occupation_skill_relations.router)
app.include_router(bulk_import.router)
app.include_router(scoring_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.get("/ping")
async def ping():
    logger.info("Ping endpoint was called.")
    return {"message": "pong"}

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Application shutting down, flushing logs...")
    logging.shutdown()