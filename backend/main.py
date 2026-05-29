"""
main.py — PropVision Backend
─────────────────────────────
App factory với lifespan context manager:
  startup  → preload tất cả .pkl vào ModelRegistry
  shutdown → log summary

Entry point:
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_ENV, APP_VERSION, CORS_ORIGINS, IS_PROD
from app.ml.registry import registry
from app.routes.predict import router as predict_router

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level   = logging.WARNING if IS_PROD else logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
    stream  = sys.stdout,
)
logger = logging.getLogger("propvision")


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan — startup / shutdown
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info(f"PropVision API v{APP_VERSION} — ENV={APP_ENV}")
    logger.info("Preloading ML models from pkl_models/...")

    t0      = time.perf_counter()
    results = registry.preload_all()       # load tất cả city × model_type
    elapsed = time.perf_counter() - t0

    loaded  = [k for k, ok in results.items() if ok]
    missing = [k for k, ok in results.items() if not ok]

    logger.info(f"Models loaded in {elapsed:.2f}s — {len(loaded)}/{len(results)} OK")
    if loaded:
        logger.info("  ✅ " + " | ".join(loaded))
    if missing:
        logger.info("  ⚠️  Mock fallback: " + " | ".join(missing))

    yield  # ← app is running

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("PropVision API shutting down.")


# ─────────────────────────────────────────────────────────────────────────────
# App factory
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "PropVision API",
    description = (
        "Real estate price prediction API for Vietnam market.\n\n"
        "Hỗ trợ 6 thành phố × 2 model types = 12 models."
    ),
    version     = APP_VERSION,
    lifespan    = lifespan,
    docs_url    = None if IS_PROD else "/docs",
    redoc_url   = None if IS_PROD else "/redoc",
)


# ─────────────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins     = CORS_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["GET", "POST"],
    allow_headers     = ["*"],
)


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    t0       = time.perf_counter()
    response = await call_next(request)
    ms       = (time.perf_counter() - t0) * 1000
    response.headers["X-Process-Time-Ms"] = f"{ms:.1f}"
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({ms:.1f}ms)")
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

# KHÔNG truyền prefix ở đây vì predict.py đã khai báo prefix="/predict" trong APIRouter
app.include_router(predict_router)


@app.get("/health", tags=["System"])
def health():
    loaded = registry.list_loaded()
    return {
        "status":        "ok",
        "version":       APP_VERSION,
        "env":           APP_ENV,
        "models_loaded": len(loaded),
        "models":        loaded,
    }


@app.get("/models", tags=["System"])
def list_models():
    """Danh sách tất cả model và trạng thái hiện tại."""
    from app.core.config import VALID_CITIES, VALID_MODEL_TYPES
    from app.ml.schemas import ModelKey

    result = []
    for city in sorted(VALID_CITIES):
        for mt in sorted(VALID_MODEL_TYPES):
            key = ModelKey(city=city, model_type=mt)
            result.append({
                "city":       city,
                "model_type": mt,
                "key":        str(key),
                "status":     "loaded" if registry.is_available(key) else "fallback_mock",
            })
    return {"models": result}
