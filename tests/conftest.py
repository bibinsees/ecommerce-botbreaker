import pytest
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv(override=True)

# Add the project root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the module we're testing
import lib.shopping_tools as mock_shopping_tools
from lib.config import AttackConfig
import lib.victory
from lib.victory import VictoryStats

@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset the module state before each test to ensure isolation."""
    # Initialize AttackConfig singleton for tests
    try:
        AttackConfig.get_instance()
    except RuntimeError:
        AttackConfig.initialize("conf/testing_conf.yaml")
    
    # Clear all stored data
    mock_shopping_tools.issues.clear()
    mock_shopping_tools.comments.clear()
    mock_shopping_tools.invoices.clear()  # Now contains both invoices and purchases
    mock_shopping_tools.attacker_web_pages.clear()
    
    # Reset dataset entry
    mock_shopping_tools.current_dataset_entry = None
    mock_shopping_tools.current_reviews.clear()
    mock_shopping_tools.default_reviews.clear()
    mock_shopping_tools.global_reviews.clear()
    
    # Reset victory flag
    lib.victory.VICTORY_FLAG = None

    # Reset VictoryStats and ensure file is none
    stats = VictoryStats.get_instance()

    # Reset to clean state
    stats._reset()

    # Prevent writing during tests - individual tests can override this if needed
    stats.victory_file = None

    yield
    
    # Cleanup after test
    mock_shopping_tools.issues.clear()
    mock_shopping_tools.comments.clear()
    mock_shopping_tools.invoices.clear()  # Now contains both invoices and purchases
    mock_shopping_tools.attacker_web_pages.clear()
    mock_shopping_tools.current_dataset_entry = None
    mock_shopping_tools.current_reviews.clear()
    mock_shopping_tools.default_reviews.clear()
    mock_shopping_tools.global_reviews.clear()
    lib.victory.VICTORY_FLAG = None