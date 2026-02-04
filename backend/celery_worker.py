import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.extensions import celery

# Initialize the Flask app to configure Celery
app = create_app()
app.app_context().push()

