from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import assets, auth, business_metrics, dashboard, nist, recommendations, reports, vulnerabilities

app = FastAPI(title="SGCM API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(vulnerabilities.router)
app.include_router(nist.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)
app.include_router(business_metrics.router)
app.include_router(reports.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
