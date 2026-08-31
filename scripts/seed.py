import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models import Base
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """
    Seed the database with initial data.
    """
    logger.info("Starting database seeding...")
    
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create test users
        test_user = User(
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            full_name="Test User",
            is_active=True,
            is_verified=True
        )
        db.add(test_user)
        db.flush()
        
        # Create sample widgets
        sample_widgets = [
            {
                "owner_id": test_user.id,
                "title": "Newsletter Signup",
                "description": "Subscribe to our newsletter for updates",
                "widget_type": "signup_form",
                "fields": ["name", "email"],
                "button_text": "Subscribe Now",
                "display_options": {
                    "theme": "light",
                    "position": "center"
                },
                "is_active": True
            },
            {
                "owner_id": test_user.id,
                "title": "Contact Us",
                "description": "Get in touch with our team",
                "widget_type": "contact_form",
                "fields": ["name", "email", "message"],
                "button_text": "Send Message",
                "display_options": {
                    "theme": "dark",
                    "position": "bottom-right"
                },
                "is_active": True
            }
        ]
        
        for widget_data in sample_widgets:
            widget = Widget(**widget_data)
            db.add(widget)
            db.flush()
            
            # Create some sample submissions
            sample_submissions = [
                {
                    "widget_id": widget.id,
                    "owner_id": test_user.id,
                    "form_data": {
                        "name": "John Doe",
                        "email": "john@example.com",
                        "message": "Hello, I'm interested in your services!"
                    },
                    "ip_address": "192.168.1.1",
                    "country": "United States",
                    "city": "New York",
                    "status": "new"
                },
                {
                    "widget_id": widget.id,
                    "owner_id": test_user.id,
                    "form_data": {
                        "name": "Jane Smith",
                        "email": "jane@example.com",
                        "message": "Please send me more information."
                    },
                    "ip_address": "192.168.1.2",
                    "country": "United Kingdom",
                    "city": "London",
                    "status": "read"
                }
            ]
            
            for submission_data in sample_submissions:
                submission = Submission(**submission_data)
                db.add(submission)
        
        db.commit()
        logger.info(f"✅ Seeded database with test user (email: test@example.com, password: test123)")
        logger.info("   - Created 2 widgets")
        logger.info("   - Created 4 sample submissions")
        logger.info("   - You can now run the application")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
