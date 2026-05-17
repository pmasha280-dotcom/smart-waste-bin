from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
from app.routers import auth, bins, floors, statistics, users, simulation
from app.services.simulation_service import simulation_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Автоматически запускаем симуляцию при старте
    logger.info("Starting simulation service...")
    import asyncio
    asyncio.create_task(simulation_service.start_simulation())
    
    yield
    
    # Shutdown
    logger.info("Stopping simulation service...")
    await simulation_service.stop_simulation()

app = FastAPI(title="Smart Bins API", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(bins.router)
app.include_router(floors.router)
app.include_router(statistics.router)
app.include_router(users.router)
app.include_router(simulation.router)

@app.get("/")
async def root():
    return {"message": "Smart Bins API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}