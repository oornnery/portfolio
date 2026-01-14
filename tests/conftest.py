"""
Pytest configuration.

Why: Sets up the Python path so tests can import from the app package.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
