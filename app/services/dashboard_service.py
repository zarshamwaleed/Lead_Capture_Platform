from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from app.models.submission import Submission
from app.models.widget import Widget
from app.schemas.dashboard import (
    DashboardStats, SubmissionTrend, WidgetPerformance,
    GeoDistribution, DashboardWidgetResponse, TimeBasedStats,
    DashboardSummary, TimeRange
)
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    def get_dashboard_stats(
        db: Session,
        user_id: int,
        time_range: TimeRange = TimeRange.MONTH
    ) -> DashboardStats:
        """
        Get comprehensive dashboard statistics for a user.
        """
        # Date range calculation
        end_date = datetime.utcnow()
        if time_range == TimeRange.TODAY:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == TimeRange.WEEK:
            start_date = end_date - timedelta(days=7)
        elif time_range == TimeRange.MONTH:
            start_date = end_date - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            start_date = end_date - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Get user's widgets
        widgets = db.query(Widget).filter(Widget.owner_id == user_id).all()
        widget_ids = [w.id for w in widgets]
        
        # Get submissions
        submissions = db.query(Submission).filter(
            Submission.owner_id == user_id
        ).all()
        
        # Filter by date range for stats
        recent_submissions = [
            s for s in submissions 
            if s.created_at >= start_date
        ]
        
        # Calculate stats
        total_submissions = len(submissions)
        total_widgets = len(widgets)
        active_widgets = len([w for w in widgets if w.is_active])
        inactive_widgets = total_widgets - active_widgets
        
        # Spam rate
        spam_count = len([s for s in submissions if s.status == "spam"])
        spam_rate = (spam_count / total_submissions * 100) if total_submissions > 0 else 0
        
        # Conversion rate (submissions that converted)
        converted = len([s for s in submissions if s.status == "converted"])
        conversion_rate = (converted / total_submissions * 100) if total_submissions > 0 else 0
        
        # Time-based counts
        submissions_today = len([
            s for s in submissions 
            if s.created_at.date() == datetime.utcnow().date()
        ])
        
        submissions_this_week = len([
            s for s in submissions 
            if s.created_at >= datetime.utcnow() - timedelta(days=7)
        ])
        
        submissions_this_month = len([
            s for s in submissions 
            if s.created_at >= datetime.utcnow() - timedelta(days=30)
        ])
        
        # Average submissions per day
        days_active = max(1, (datetime.utcnow() - start_date).days)
        avg_submissions_per_day = total_submissions / days_active
        
        # Top widget
        top_widget = None
        if widget_ids:
            widget_counts = {}
            for s in submissions:
                widget_counts[s.widget_id] = widget_counts.get(s.widget_id, 0) + 1
            
            if widget_counts:
                top_widget_id = max(widget_counts, key=widget_counts.get)
                top_widget_widget = db.query(Widget).filter(Widget.id == top_widget_id).first()
                if top_widget_widget:
                    top_widget = {
                        "id": top_widget_widget.id,
                        "title": top_widget_widget.title,
                        "count": widget_counts[top_widget_id]
                    }
        
        # Unique vs repeat visitors
        ip_addresses = set()
        repeat_ips = []
        for s in submissions:
            if s.ip_address:
                if s.ip_address in ip_addresses:
                    repeat_ips.append(s.ip_address)
                else:
                    ip_addresses.add(s.ip_address)
        
        unique_visitors = len(ip_addresses)
        repeat_visitors = len(set(repeat_ips))
        
        return DashboardStats(
            total_submissions=total_submissions,
            total_widgets=total_widgets,
            conversion_rate=conversion_rate,
            spam_rate=spam_rate,
            submissions_today=submissions_today,
            submissions_this_week=submissions_this_week,
            submissions_this_month=submissions_this_month,
            active_widgets=active_widgets,
            inactive_widgets=inactive_widgets,
            top_widget=top_widget,
            avg_submissions_per_day=avg_submissions_per_day,
            unique_visitors=unique_visitors,
            repeat_visitors=repeat_visitors
        )
    
    @staticmethod
    def get_submission_trends(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[SubmissionTrend]:
        """
        Get submission trends over time.
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        submissions = db.query(Submission).filter(
            Submission.owner_id == user_id,
            Submission.created_at >= start_date
        ).order_by(Submission.created_at).all()
        
        trends = []
        cumulative = 0
        
        for i in range(days):
            current_date = datetime.utcnow().date() - timedelta(days=i)
            day_submissions = [
                s for s in submissions 
                if s.created_at.date() == current_date
            ]
            count = len(day_submissions)
            cumulative += count
            
            trends.append(SubmissionTrend(
                date=current_date,
                count=count,
                cumulative=cumulative
            ))
        
        return sorted(trends, key=lambda x: x.date)
    
    @staticmethod
    def get_widget_performance(
        db: Session,
        user_id: int,
        widget_id: Optional[int] = None
    ) -> List[WidgetPerformance]:
        """
        Get performance metrics for widgets.
        """
        query = db.query(Widget).filter(Widget.owner_id == user_id)
        if widget_id:
            query = query.filter(Widget.id == widget_id)
        
        widgets = query.all()
        performances = []
        
        for widget in widgets:
            submissions = db.query(Submission).filter(
                Submission.widget_id == widget.id
            ).all()
            
            total = len(submissions)
            spam_count = len([s for s in submissions if s.status == "spam"])
            converted = len([s for s in submissions if s.status == "converted"])
            
            conversion_rate = (converted / total * 100) if total > 0 else 0
            
            # Get submissions by day
            last_30_days = []
            for i in range(30):
                day = datetime.utcnow().date() - timedelta(days=i)
                count = len([
                    s for s in submissions 
                    if s.created_at.date() == day
                ])
                last_30_days.append(SubmissionTrend(
                    date=day,
                    count=count,
                    cumulative=sum([len([s for s in submissions if s.created_at.date() <= day])])
                ))
            
            last_submission = submissions[-1].created_at if submissions else None
            
            performances.append(WidgetPerformance(
                widget_id=widget.id,
                widget_title=widget.title,
                total_submissions=total,
                conversion_rate=conversion_rate,
                spam_count=spam_count,
                active=widget.is_active,
                last_submission=last_submission,
                submissions_by_day=sorted(last_30_days, key=lambda x: x.date)
            ))
        
        return sorted(performances, key=lambda x: x.total_submissions, reverse=True)
    
    @staticmethod
    def get_geo_distribution(
        db: Session,
        user_id: int
    ) -> List[GeoDistribution]:
        """
        Get geographical distribution of submissions.
        """
        submissions = db.query(Submission).filter(
            Submission.owner_id == user_id,
            Submission.country.isnot(None)
        ).all()
        
        total = len(submissions)
        if total == 0:
            return []
        
        # Count by country
        country_counts = {}
        city_counts = {}
        
        for s in submissions:
            if s.country:
                country_counts[s.country] = country_counts.get(s.country, 0) + 1
                
                if s.city:
                    key = f"{s.country}:{s.city}"
                    city_counts[key] = city_counts.get(key, 0) + 1
        
        # Build distribution
        distribution = []
        for country, count in country_counts.items():
            cities = []
            for key, city_count in city_counts.items():
                if key.startswith(f"{country}:"):
                    city_name = key.split(":", 1)[1]
                    cities.append({
                        "city": city_name,
                        "count": city_count,
                        "percentage": (city_count / total) * 100
                    })
            
            distribution.append(GeoDistribution(
                country=country,
                count=count,
                percentage=(count / total) * 100,
                cities=sorted(cities, key=lambda x: x["count"], reverse=True)[:5]
            ))
        
        return sorted(distribution, key=lambda x: x.count, reverse=True)
    
    @staticmethod
    def get_hourly_distribution(
        db: Session,
        user_id: int
    ) -> List[TimeBasedStats]:
        """
        Get submission distribution by hour of day.
        """
        submissions = db.query(Submission).filter(
            Submission.owner_id == user_id
        ).all()
        
        hourly_counts = {}
        for s in submissions:
            hour = s.created_at.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        return [
            TimeBasedStats(
                hour=hour,
                submissions=count,
                hour_of_day=f"{hour:02d}:00 - {hour:02d}:59"
            )
            for hour, count in sorted(hourly_counts.items())
        ]
    
    @staticmethod
    def get_dashboard_summary(
        db: Session,
        user_id: int,
        time_range: TimeRange = TimeRange.MONTH
    ) -> DashboardSummary:
        """
        Get complete dashboard summary.
        """
        stats = DashboardService.get_dashboard_stats(db, user_id, time_range)
        trends = DashboardService.get_submission_trends(db, user_id)
        top_widgets = DashboardService.get_widget_performance(db, user_id)[:5]
        geo_distribution = DashboardService.get_geo_distribution(db, user_id)
        hourly_distribution = DashboardService.get_hourly_distribution(db, user_id)
        
        # Convert to widget response
        widget_responses = [
            DashboardWidgetResponse(
                id=w.widget_id,
                title=w.widget_title,
                total_submissions=w.total_submissions,
                spam_count=w.spam_count,
                conversion_rate=w.conversion_rate,
                is_active=w.active
            )
            for w in top_widgets
        ]
        
        return DashboardSummary(
            stats=stats,
            trends=trends,
            top_widgets=widget_responses,
            geo_distribution=geo_distribution,
            hourly_distribution=hourly_distribution
        )
