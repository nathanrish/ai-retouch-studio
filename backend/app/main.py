from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints.retouch import router as retouch_router
from .api.endpoints.luts import router as luts_router
from .api.endpoints.segmentation import router as segmentation_router
from .services.ai_service import get_ai_service
from .core.config import settings

app = FastAPI(title="AI Retouch Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(luts_router, prefix=settings.API_PREFIX)
app.include_router(retouch_router, prefix=settings.API_PREFIX)
app.include_router(segmentation_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    # Warm up AI model asynchronously
    ai = get_ai_service()
    await ai.warmup()


@app.get("/")
async def root():
    return {"service": "ai-retouch-studio", "status": "ok"}


@app.get(f"{settings.API_PREFIX}/health")
async def api_health():
    ai = get_ai_service()
    health = await ai.health()
    return {"status": "ok", "device": health.get("device", "cpu")}
