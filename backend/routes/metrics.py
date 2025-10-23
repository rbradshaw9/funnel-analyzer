"""Public metrics endpoints for marketing surfaces."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db_session
from ..models.database import Analysis, AnalysisPage
from ..models.schemas import PublicStatsResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/stats", response_model=PublicStatsResponse)
async def get_public_stats(session: AsyncSession = Depends(get_db_session)) -> PublicStatsResponse:
    """Return aggregate statistics for frontend displays."""

    analyses_result = await session.execute(select(func.count()).select_from(Analysis))
    analyses_total = analyses_result.scalar_one()

    pages_result = await session.execute(select(func.count()).select_from(AnalysisPage))
    pages_total = pages_result.scalar_one()

    logger.debug("Fetched public stats: analyses=%s pages=%s", analyses_total, pages_total)

    return PublicStatsResponse(analyses_run=int(analyses_total or 0), pages_analyzed=int(pages_total or 0))
