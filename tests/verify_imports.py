
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Verifying imports...")

try:
    import app.main
    print("✅ app.main imported successfully")
except Exception as e:
    print(f"❌ Failed to import app.main: {e}")

modules_to_check = [
    "app.api.routers.health",
    "app.api.routers.sales",
    "app.api.routers.pipeline",
    "app.api.routers.inventory",
    "app.core.scraper_utils",
    "app.db.session",
]

for module in modules_to_check:
    try:
        __import__(module)
        print(f"✅ {module} imported successfully")
    except Exception as e:
        print(f"❌ Failed to import {module}: {e}")

print("Import verification complete.")
