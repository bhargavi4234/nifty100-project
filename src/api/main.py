import logging
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "db" / "nifty100.db"

VERSION = "1.0.0"

START_TIME = time.time()


# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------
# SQLite connection
# ------------------------------------------------------------


def get_db_connection():
    "Get db connection."
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------------------------------------------
# FastAPI application
# ------------------------------------------------------------

app = FastAPI(
    title="Nifty 100 Analytics API",
    version=VERSION,
    description="FastAPI backend for Nifty 100 financial analytics.",
)


# ------------------------------------------------------------
# CORS
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Request logging middleware
# ------------------------------------------------------------


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    "Request logging middleware."
    start = time.perf_counter()

    response = await call_next(request)

    elapsed = time.perf_counter() - start

    logger.info(
        "%s %s -> %s | %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )

    response.headers["X-Response-Time"] = f"{elapsed:.6f}"

    return response


# ------------------------------------------------------------
# Health endpoint
# ------------------------------------------------------------


@app.get(
    "/api/v1/health",
    tags=["Health"],
)
def health():
    "Health."

    conn = get_db_connection()

    tables = [
        "companies",
        "sectors",
        "peer_groups",
        "analysis",
        "prosandcons",
        "documents",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "financial_ratios",
    ]

    row_counts = {}

    try:
        for table in tables:
            result = conn.execute(f"SELECT COUNT(*) FROM [{table}]").fetchone()

            row_counts[table] = result[0]

    finally:
        conn.close()

    return {
        "status": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": round(
            time.time() - START_TIME,
            2,
        ),
        "version": VERSION,
    }


# ------------------------------------------------------------
# Routers
# ------------------------------------------------------------

from src.api.routers import (
    companies,
    documents,
    peers,
    portfolio,
    screener,
    sectors,
    valuation,
)
from src.api.routers import (
    health as health_router,
)

app.include_router(
    companies.router,
    prefix="/api/v1",
)

app.include_router(
    screener.router,
    prefix="/api/v1",
)

app.include_router(
    sectors.router,
    prefix="/api/v1",
)

app.include_router(
    peers.router,
    prefix="/api/v1",
)

app.include_router(
    valuation.router,
    prefix="/api/v1",
)

app.include_router(
    portfolio.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    health_router.router,
    prefix="/api/v1",
)
