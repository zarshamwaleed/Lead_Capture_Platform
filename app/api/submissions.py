from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.core.spam_protection import SpamProtection
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
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/submissions", tags=["Public Submissions"])

# Apply rate limiting to submission creation
@router.post(
    "/", 
    response_model=SubmissionResponse, 
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")  # 10 requests per minute per IP
@limiter.limit("50/hour")    # 50 requests per hour per IP
async def create_submission(
    request: Request,
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to submit a form with rate limiting and spam protection.
    """
    # Get client IP
    client_ip = request.client.host if request.client else None
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    
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
        
        # Check for honeypot (already handled by Pydantic validator)
        # The validator in SubmissionCreate handles honeypot validation
        
        # Enhanced spam check
        is_spam, spam_reasons = SpamProtection.check_spam(submission_data.data)
        
        if is_spam:
            logger.warning(f"Spam submission blocked from {client_ip}: {spam_reasons}")
            # Log spam but return success to confuse bots
            # We could also store it as spam status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid form data"
            )
        
        # Validate email if present
        if 'email' in submission_data.data:
            is_valid, reason = SpamProtection.validate_email(submission_data.data['email'])
            if not is_valid:
                logger.warning(f"Invalid email from {client_ip}: {reason}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid email: {reason}"
                )
        
        # Validate phone if present
        if 'phone' in submission_data.data:
            is_valid, reason = SpamProtection.validate_phone(submission_data.data['phone'])
            if not is_valid:
                logger.warning(f"Invalid phone from {client_ip}: {reason}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid phone: {reason}"
                )
        
        # Check for duplicate submissions (within last 5 minutes)
        duplicate_check = db.query(Submission).filter(
            Submission.widget_id == widget.id,
            Submission.ip_address == client_ip,
            Submission.created_at > datetime.utcnow() - timedelta(minutes=5)
        ).first()
        
        # If duplicate found, check if it has the same data
        if duplicate_check:
            # Compare form data (simplified check)
            if duplicate_check.form_data == submission_data.data:
                logger.info(f"Duplicate submission blocked from {client_ip}")
                # Return success to hide detection
                return duplicate_check
        
        # Create submission
        submission = Submission(
            widget_id=widget.id,
            owner_id=widget.owner_id,
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
@limiter.limit("30/minute")  # Stricter limit for API users
async def get_submissions(
    request: Request,
    widget_id: Optional[int] = None,
    status: Optional[SubmissionStatus] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get submissions for the authenticated user with rate limiting.
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
