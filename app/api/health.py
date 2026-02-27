from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.dependencies import limiter

router = APIRouter()


@router.get("/health", response_class=JSONResponse, include_in_schema=False)
@limiter.exempt
async def health() -> dict[str, str]:
    return {"status": "ok"}
