from fastapi import APIRouter

from app.api.routes import agencies, bootstrap, cases, dashboard, requests, sources

api_router = APIRouter()
api_router.include_router(agencies.router, prefix="/agencies", tags=["agencies"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(requests.router, prefix="/records-requests", tags=["records requests"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(bootstrap.router, prefix="/bootstrap", tags=["local bootstrap"])
api_router.include_router(sources.router, prefix="/sources", tags=["discovery sources"])
