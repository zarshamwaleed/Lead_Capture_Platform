from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission
from app.schemas.submission import (
    SubmissionCreate, 
    SubmissionResponse, 
    SubmissionUpdate, 
    SubmissionStats,
    SubmissionStatus
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/submissions", tags=["Public Submissions"])

@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    request: Request,
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to submit a form.
    No authentication required - this is for visitors on external websites.
    """
    try:
        # Get the widget
        widget = db.query(Widget).filter(
            Widget.id == submission_data.widget_id,
            Widget.is_active == True
        ).first()
        
        if not widget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found or inactive"
            )
        
        # Get client IP
        client_ip = request.client.host if request.client else None
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        
        # Create submission
        submission = Submission(
            widget_id=widget.id,
            owner_id=widget.owner_id,  # Link to widget owner
            form_data=submission_data.data,
            ip_address=client_ip,
            status=SubmissionStatus.NEW.value
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        logger.info(f"New submission received for widget {widget.id} from IP {client_ip}")
        
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process submission"
        )

# Protected endpoints - require authentication
@router.get("/", response_model=List[SubmissionResponse])
async def get_submissions(
    widget_id: Optional[int] = None,
    status: Optional[SubmissionStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get submissions for the authenticated user.
    """
    query = db.query(Submission).filter(Submission.owner_id == current_user.id)
    
    if widget_id:
        query = query.filter(Submission.widget_id == widget_id)
    
    if status:
        query = query.filter(Submission.status == status.value)
    
    submissions = query.order_by(Submission.created_at.desc()).offset(skip).limit(limit).all()
    
    return submissions

@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific submission.
    """
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.owner_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or you don't have permission to access it"
        )
    
    return submission

@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    update_data: SubmissionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update submission status.
    """
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.owner_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found or you don't have permission to access it"
        )
    
    submission.status = update_data.status.value
    db.commit()
    db.refresh(submission)
    
    logger.info(f"Submission {submission.id} status updated to {submission.status}")
    
    return submission

@router.get("/stats/dashboard", response_model=SubmissionStats)
async def get_submission_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get submission statistics for the authenticated user.
    """
    # Get all submissions for user
    submissions = db.query(Submission).filter(Submission.owner_id == current_user.id).all()
    
    # Count by status
    status_counts = {
        SubmissionStatus.NEW.value: 0,
        SubmissionStatus.READ.value: 0,
        SubmissionStatus.CONTACTED.value: 0,
        SubmissionStatus.CONVERTED.value: 0,
        SubmissionStatus.SPAM.value: 0
    }
    
    for submission in submissions:
        if submission.status in status_counts:
            status_counts[submission.status] += 1
    
    # Count by country
    country_counts = {}
    for submission in submissions:
        if submission.country:
            country_counts[submission.country] = country_counts.get(submission.country, 0) + 1
    
    # Count by widget
    widget_counts = {}
    for submission in submissions:
        widget_counts[str(submission.widget_id)] = widget_counts.get(str(submission.widget_id), 0) + 1
    
    # Last 7 days
    last_7_days = []
    for i in range(7):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = sum(1 for s in submissions if s.created_at.date() == day)
        last_7_days.append({
            "date": day.isoformat(),
            "count": count
        })
    
    return SubmissionStats(
        total=len(submissions),
        new=status_counts[SubmissionStatus.NEW.value],
        read=status_counts[SubmissionStatus.READ.value],
        contacted=status_counts[SubmissionStatus.CONTACTED.value],
        converted=status_counts[SubmissionStatus.CONVERTED.value],
        spam=status_counts[SubmissionStatus.SPAM.value],
        by_country=country_counts,
        by_widget=widget_counts,
        last_7_days=last_7_days
    )
