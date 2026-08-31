from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class TimeRange(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    CUSTOM = "custom"

class DashboardStats(BaseModel):
    total_submissions: int
    total_widgets: int
    conversion_rate: float
    spam_rate: float
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int
    active_widgets: int
    inactive_widgets: int
    top_widget: Optional[Dict[str, Any]] = None
    avg_submissions_per_day: float
    unique_visitors: int
    repeat_visitors: int

class SubmissionTrend(BaseModel):
    date: date
    count: int
    cumulative: int

class WidgetPerformance(BaseModel):
    widget_id: int
    widget_title: str
    total_submissions: int
    conversion_rate: float
    spam_count: int
    active: bool
    last_submission: Optional[datetime] = None
    submissions_by_day: List[SubmissionTrend]

class GeoDistribution(BaseModel):
    country: str
    count: int
    percentage: float
    cities: List[Dict[str, Any]]

class TimeBasedStats(BaseModel):
    hour: int
    submissions: int
    hour_of_day: str

class DashboardWidgetResponse(BaseModel):
    id: int
    title: str
    total_submissions: int
    spam_count: int
    conversion_rate: float
    is_active: bool

class DashboardSummary(BaseModel):
    stats: DashboardStats
    trends: List[SubmissionTrend]
    top_widgets: List[DashboardWidgetResponse]
    geo_distribution: List[GeoDistribution]
    hourly_distribution: List[TimeBasedStats]
