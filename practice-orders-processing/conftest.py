import sys
from pathlib import Path

# Add the practice-orders-processing directory to Python path
# so that 'src' module can be imported reliably from any working directory.
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
