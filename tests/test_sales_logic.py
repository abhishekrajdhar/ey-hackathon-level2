
from app.db.session import SessionLocal
from app.db import models
from app.domain.agents.technical_agent import TechnicalAgent
from app.domain.agents.pricing_agent import PricingAgent
from sqlalchemy import select

def test_sales_logic():
    db = SessionLocal()
    tech_agent = TechnicalAgent()
    pricing_agent = PricingAgent()
    
    try:
        print("🧪 Testing Sales Agent Logic (Technical & Pricing)...")
        
        # Fetch RFP-002
        rfp = db.execute(select(models.RFP).where(models.RFP.external_id == "RFP-002")).scalar_one_or_none()
        if not rfp:
            print("❌ RFP-002 not found!")
            return

        print(f"   Analyzing RFP: {rfp.title}")
        
        # 1. Technical Matching
        matches = tech_agent.process_rfp(db, rfp)
        
        # 2. Pricing
        pricing_summary = pricing_agent.price_rfp(db, matches, rfp.tests)
        
        print("\n   📊 Pricing Summary:")
        print(f"      Total Material Cost: ${pricing_summary.total_material_cost}")
        print(f"      Total Tests Cost: ${pricing_summary.total_tests_cost}")
        print(f"      Grand Total: ${pricing_summary.grand_total}")

        # Verify Line Items
        for match in matches:
            print(f"\n   📋 Line Item {match.line_id}: {match.description}")
            print(f"      Selected SKU: {match.selected_sku.sku if match.selected_sku else 'None'}")
            
            # Find price row
            row = next((r for r in pricing_summary.rows if r.line_id == match.line_id), None)
            if row:
                print(f"      Unit Price: ${row.unit_price}")
                print(f"      Material Cost: ${row.material_cost}")
            
            if match.line_id == 1:
                # Expect Aluminum (AP-CABLE-003) @ $420
                if match.selected_sku.sku == "AP-CABLE-003" and row.unit_price == 420.0:
                     print("      ✅ PASS: Al Cable matched and priced correctly.")
                else:
                     print(f"      ❌ FAIL: Incorrect match or price. Got {match.selected_sku.sku}, ${row.unit_price}")

            elif match.line_id == 2:
                # Expect HV (HV-CABLE-001) @ $3500
                 if match.selected_sku.sku == "HV-CABLE-001" and row.unit_price == 3500.0:
                     print("      ✅ PASS: HV Cable matched and priced correctly.")
                 else:
                     print(f"      ❌ FAIL: Incorrect match or price. Got {match.selected_sku.sku}, ${row.unit_price}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_sales_logic()
