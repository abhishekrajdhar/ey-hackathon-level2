
from app.domain.agents.sales_agent import SalesAgent
from app.db.session import SessionLocal

def verify_global_tenders():
    print("🌍 Verifying 'global-tenders.com' data access...")
    
    db = SessionLocal()
    agent = SalesAgent()
    
    # We query for the EXACT url used in seed_data: "http://global-tenders.com"
    # Note: user asked about https, but seed data has http. We check http first.
    target_urls = ["http://global-tenders.com"]
    
    try:
        # scan_rfps calls repositories.get_rfps_due_within
        rfps = agent.scan_rfps(db, target_urls, within_months=24) # Long duration to catch all
        
        print(f"   🔍 Querying for: {target_urls}")
        print(f"   📊 Found {len(rfps)} RFPs.")
        
        for rfp in rfps:
            print(f"      - [{rfp.id}] {rfp.title} (Source: {rfp.source_url})")
            
        if len(rfps) > 0:
            print("   ✅ SUCCESS: Global Tenders data is accessible.")
        else:
             print("   ❌ FAILURE: No RFPs found for this URL.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_global_tenders()
