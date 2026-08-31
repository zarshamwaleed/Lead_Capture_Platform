import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_tests():
    """Run all tests."""
    logger.info("Running tests...")
    
    # Set test environment
    os.environ['TESTING'] = 'True'
    
    # Run pytest
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--maxfail=1",
        "--disable-warnings"
    ])
    
    if exit_code == 0:
        logger.info("All tests passed!")
    else:
        logger.error("Some tests failed!")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())