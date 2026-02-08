import sys
from pathlib import Path

# Root directory of the workspace
root_dir = Path(__file__).parent

# List of subprojects that need their directories added to sys.path
# so their 'src' modules can be imported
subprojects = [
    "practice-orders-processing",
    "user-analytics-api",
    "document-editor",
]

# Add each subproject directory to Python path
# This runs immediately when conftest.py is imported
for subproject in subprojects:
    subproject_path = root_dir / subproject
    if subproject_path.exists() and str(subproject_path) not in sys.path:
        sys.path.insert(0, str(subproject_path))
