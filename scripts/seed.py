import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from app.models import User, Widget, Submission
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """
    Seed the database with initial data.
    """
    logger.info("Starting database seeding...")
    
    db = SessionLocal()
    
    try:
        # Create test users
        test_user = User(
            email="test@example.com",
            password="test123",
            full_name="Test User",
        )
        test_user.is_verified = True
        db.add(test_user)
        db.flush()
        
        admin_user = User(
            email="admin@example.com",
            password="admin123",
            full_name="Admin User",
        )
        admin_user.is_verified = True
        db.add(admin_user)
        db.flush()
        
        # Create sample widgets for test user
        sample_widgets = [
            Widget(
                owner_id=test_user.id,
                title="Newsletter Signup",
                description="Subscribe to our newsletter for updates",
                widget_type="signup_form",
                fields=["name", "email"],
                button_text="Subscribe Now",
                display_options={
                    "theme": "light",
                    "position": "center",
                    "backgroundColor": "#ffffff",
                    "textColor": "#000000"
                },
                is_active=True
            ),
            Widget(
                owner_id=test_user.id,
                title="Contact Us",
                description="Get in touch with our team",
                widget_type="contact_form",
                fields=["name", "email", "message"],
                button_text="Send Message",
                display_options={
                    "theme": "dark",
                    "position": "bottom-right",
                    "backgroundColor": "#1a1a1a",
                    "textColor": "#ffffff"
                },
                is_active=True
            )
        ]
        
        for widget_data in sample_widgets:
            db.add(widget_data)
            db.flush()
            
            # Create some sample submissions
            sample_submissions = [
                Submission(
                    widget_id=widget_data.id,
                    owner_id=test_user.id,
                    form_data={
                        "name": "John Doe",
                        "email": "john@example.com",
                        "message": "Hello, I'm interested in your services!"
                    } if widget_data.widget_type == "contact_form" else {
                        "name": "Jane Smith",
                        "email": "jane@example.com"
                    },
                    ip_address="192.168.1.1",
                    country="United States",
                    city="New York",
                    status="new"
                ),
                Submission(
                    widget_id=widget_data.id,
                    owner_id=test_user.id,
                    form_data={
                        "name": "Bob Wilson",
                        "email": "bob@example.com",
                        "message": "I'd like to schedule a demo."
                    } if widget_data.widget_type == "contact_form" else {
                        "name": "Alice Johnson",
                        "email": "alice@example.com"
                    },
                    ip_address="192.168.1.2",
                    country="United Kingdom",
                    city="London",
                    status="read"
                )
            ]
            
            for submission_data in sample_submissions:
                db.add(submission_data)
        
        db.commit()
        
        logger.info("✅ Database seeded successfully!")
        logger.info(f"   - Created 2 users:")
        logger.info(f"     • test@example.com (password: test123)")
        logger.info(f"     • admin@example.com (password: admin123)")
        logger.info(f"   - Created {len(sample_widgets)} widgets for test user")
        logger.info(f"   - Created 4 sample submissions")
        logger.info(f"   - You can now run the application")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
