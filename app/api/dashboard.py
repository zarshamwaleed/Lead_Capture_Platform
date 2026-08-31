from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.rate_limiter import limiter
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStats, DashboardSummary, WidgetPerformance,
    GeoDistribution, SubmissionTrend, TimeRange
)
from app.services.dashboard_service import DashboardService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
@limiter.limit("30/minute")
async def get_dashboard_stats(
    request: Request,  # Added request parameter
    time_range: TimeRange = Query(default=TimeRange.MONTH, description="Time range for stats"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics.
    """
    try:
        stats = DashboardService.get_dashboard_stats(db, current_user.id, time_range)
        return stats
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve dashboard stats"
        )

@router.get("/summary", response_model=DashboardSummary)
@limiter.limit("30/minute")
async def get_dashboard_summary(
    request: Request,  # Added request parameter
    time_range: TimeRange = Query(default=TimeRange.MONTH, description="Time range for data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get complete dashboard summary with all metrics.
    """
    try:
        summary = DashboardService.get_dashboard_summary(db, current_user.id, time_range)
        return summary
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve dashboard summary"
        )

@router.get("/trends", response_model=List[SubmissionTrend])
@limiter.limit("30/minute")
async def get_submission_trends(
    request: Request,  # Added request parameter
    days: int = Query(default=30, ge=1, le=365, description="Number of days to show"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get submission trends over time.
    """
    try:
        trends = DashboardService.get_submission_trends(db, current_user.id, days)
        return trends
    except Exception as e:
        logger.error(f"Error getting trends: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve trends"
        )

@router.get("/widgets/performance", response_model=List[WidgetPerformance])
@limiter.limit("30/minute")
async def get_widget_performance(
    request: Request,  # Added request parameter
    widget_id: Optional[int] = Query(None, description="Filter by widget ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for widgets.
    """
    try:
        performance = DashboardService.get_widget_performance(db, current_user.id, widget_id)
        return performance
    except Exception as e:
        logger.error(f"Error getting widget performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve widget performance"
        )

@router.get("/geo", response_model=List[GeoDistribution])
@limiter.limit("30/minute")
async def get_geo_distribution(
    request: Request,  # Added request parameter
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get geographical distribution of submissions.
    """
    try:
        distribution = DashboardService.get_geo_distribution(db, current_user.id)
        return distribution
    except Exception as e:
        logger.error(f"Error getting geo distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve geo distribution"
        )

@router.get("/hourly", response_model=List[Dict[str, Any]])
@limiter.limit("30/minute")
async def get_hourly_distribution(
    request: Request,  # Added request parameter
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get submission distribution by hour.
    """
    try:
        hourly = DashboardService.get_hourly_distribution(db, current_user.id)
        return [h.model_dump() for h in hourly]
    except Exception as e:
        logger.error(f"Error getting hourly distribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve hourly distribution"
        )
