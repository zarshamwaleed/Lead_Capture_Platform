from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.widget import Widget
from app.schemas.widget import WidgetCreate, WidgetUpdate, WidgetResponse, WidgetPublicConfig
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/widgets", tags=["Widgets"])

@router.post("/", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
async def create_widget(
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new widget for the authenticated user.
    """
    try:
        widget = Widget(
            owner_id=current_user.id,
            title=widget_data.title,
            description=widget_data.description,
            widget_type=widget_data.widget_type.value,
            fields=widget_data.fields,
            button_text=widget_data.button_text,
            display_options=widget_data.display_options,
            is_active=widget_data.is_active
        )
        
        db.add(widget)
        db.commit()
        db.refresh(widget)
        
        # Generate embed snippet
        embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
        
        logger.info(f"Widget created: {widget.title} (ID: {widget.id}) by user {current_user.email}")
        
        response = WidgetResponse.model_validate(widget)
        response.embed_snippet = embed_snippet
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create widget"
        )

@router.get("/", response_model=List[WidgetResponse])
async def get_widgets(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all widgets for the authenticated user.
    """
    query = db.query(Widget).filter(Widget.owner_id == current_user.id)
    
    if is_active is not None:
        query = query.filter(Widget.is_active == is_active)
    
    widgets = query.offset(skip).limit(limit).all()
    
    # Add embed snippets to each widget
    response_widgets = []
    for widget in widgets:
        widget_response = WidgetResponse.model_validate(widget)
        widget_response.embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
        response_widgets.append(widget_response)
    
    return response_widgets

@router.get("/{widget_id}", response_model=WidgetResponse)
async def get_widget(
    widget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific widget by ID.
    """
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.owner_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or you don't have permission to access it"
        )
    
    response = WidgetResponse.model_validate(widget)
    response.embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
    return response

@router.put("/{widget_id}", response_model=WidgetResponse)
async def update_widget(
    widget_id: int,
    widget_data: WidgetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a widget.
    """
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.owner_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or you don't have permission to access it"
        )
    
    try:
        # Update only provided fields
        update_data = widget_data.model_dump(exclude_unset=True)
        
        # Handle widget_type specially
        if 'widget_type' in update_data and update_data['widget_type']:
            update_data['widget_type'] = update_data['widget_type'].value
        
        for field, value in update_data.items():
            setattr(widget, field, value)
        
        db.commit()
        db.refresh(widget)
        
        logger.info(f"Widget updated: {widget.title} (ID: {widget.id})")
        
        response = WidgetResponse.model_validate(widget)
        response.embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
        return response
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update widget"
        )

@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a widget.
    """
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.owner_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or you don't have permission to access it"
        )
    
    try:
        db.delete(widget)
        db.commit()
        logger.info(f"Widget deleted: {widget.title} (ID: {widget.id})")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting widget: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete widget"
        )

@router.post("/{widget_id}/toggle", response_model=WidgetResponse)
async def toggle_widget_active(
    widget_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle widget active status.
    """
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.owner_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or you don't have permission to access it"
        )
    
    widget.is_active = not widget.is_active
    db.commit()
    db.refresh(widget)
    
    status_text = "activated" if widget.is_active else "deactivated"
    logger.info(f"Widget {status_text}: {widget.title} (ID: {widget.id})")
    
    response = WidgetResponse.model_validate(widget)
    response.embed_snippet = f'<script src="http://localhost:8000/widget.js?id={widget.id}"></script>'
    return response

# Public endpoint for widget configuration (no authentication required)
@router.get("/public/{widget_id}/config", response_model=WidgetPublicConfig)
async def get_widget_public_config(
    widget_id: int,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to get widget configuration for embedding.
    No authentication required - this is for the widget to load.
    """
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.is_active == True
    ).first()
    
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or inactive"
        )
    
    return WidgetPublicConfig.model_validate(widget)
