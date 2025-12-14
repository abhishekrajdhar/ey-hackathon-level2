
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings

client = TestClient(app)
settings = get_settings()

def test_sales_scan_endpoint():
    print("🧪 Testing API Endpoint: /sales/scan")
    
    # 1. Test URLs matching seeded RFPs
    params = [
        ("urls", "https://example-lstk1.com/tenders"),
        ("urls", "https://power-grid-west.com/procurement")
    ]
    
    url = f"{settings.api_v1_prefix}/sales/scan"
    response = client.get(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ API Request Failed: {response.status_code}")
        print(response.json())
        return

    data = response.json()
    print(f"✅ API Status: {response.status_code}")
    print(f"📊 RFPs Found: {len(data)}")
    
    rfp_titles = [item['title'] for item in data]
    
    # Check for RFP-001 (Copper)
    if "Supply of LV Cables for Metro Depot" in rfp_titles:
        print("   ✅ Found: Supply of LV Cables for Metro Depot")
    else:
        print("   ❌ Missing: Supply of LV Cables for Metro Depot")

    # Check for RFP-002 (Al/HV)
    if "Annual Cable Supply - West Zone" in rfp_titles:
        print("   ✅ Found: Annual Cable Supply - West Zone")
    else:
        print("   ❌ Missing: Annual Cable Supply - West Zone")

if __name__ == "__main__":
    test_sales_scan_endpoint()
