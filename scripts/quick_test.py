import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ['TESTING'] = 'True'

from app.core.database import setup_test_db
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission

def run_quick_tests():
    """Run quick tests without pytest."""
    print("=== QUICK TESTS ===")
    
    try:
        # Test database setup
        print("1. Testing database setup...")
        setup_test_db()
        print("   Database setup successful")
        
        # Test user creation
        print("2. Testing user model...")
        user = User(
            email="test@example.com",
            password="test123",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.verify_password("test123") == True
        print("   User model works")
        
        # Test widget creation
        print("3. Testing widget model...")
        widget = Widget(
            owner_id=1,
            title="Test Widget",
            widget_type="signup_form",
            fields=["name", "email"],
            button_text="Submit",
            is_active=True
        )
        assert widget.title == "Test Widget"
        assert widget.is_active == True
        print("   Widget model works")
        
        # Test submission creation
        print("4. Testing submission model...")
        submission = Submission(
            widget_id=1,
            owner_id=1,
            form_data={"name": "John Doe", "email": "john@example.com"},
            ip_address="127.0.0.1",
            status="new"
        )
        assert submission.form_data["name"] == "John Doe"
        assert submission.status == "new"
        print("   Submission model works")
        
        print("All quick tests passed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)