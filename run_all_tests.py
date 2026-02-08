
#!/usr/bin/env python
"""Run all tests in the workspace."""
import subprocess
import sys

test_paths = [
    "tests/",
    "introduction/",
    "practice-orders-processing/tests/",
    "user-analytics-api/tests/",
]

failed = False
for path in test_paths:
    print(f"\n{'='*60}")
    print(f"Running tests in: {path}")
    print('='*60)
    # Use pytest command directly, which will use the active environment
    result = subprocess.run(["pytest", path, "-v"], shell=True)
    if result.returncode != 0:
        failed = True

print(f"\n{'='*60}")
if failed:
    print("Some tests failed!")
else:
    print("All tests passed!")
print('='*60)

sys.exit(1 if failed else 0)
