
from app.db.session import SessionLocal
from app.db import models
from app.domain.agents.sales_agent import SalesAgent
from app.domain.agents.main_agent import MainAgent
from app.domain.agents.technical_agent import TechnicalAgent
from app.domain.agents.pricing_agent import PricingAgent
from app.models.schemas import RFPSummary
from sqlalchemy import select
import json

def verify_ai_workflows():
    print("🤖 Verifying Advanced AI Workflows...\n")
    sales_agent = SalesAgent()
    main_agent = MainAgent()
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Verify Unstructured Text Parsing (PDF/Text -> JSON)
        # ---------------------------------------------------------
        print("🧪 1. Testing Unstructured Text Parsing...")
        mock_rfp_text = """
        TENDER NOTICE: PROCUREMENT OF CABLES
        Ref: MOCK-TENDER-2025
        Due Date: 2025-12-31
        
        Scope of Work:
        Supply of approximately 5000 meters of 1.1kV, 4-core, 16 sqmm Copper XLPE Armoured Cable.
        Also required: 2000 meters of 11kV, 3-core, 240 sqmm Copper XLPE Cable.
        
        Testing:
        Routine electrical tests and Partial Discharge test required.
        """
        
        print("   Thinking (Parsing text)...")
        parsed_data = sales_agent._llm_parse_rfp("Mock Tender Title", mock_rfp_text)
        
        if parsed_data:
            print("   ✅ Parsing Successful!")
            print(f"      - Date Found: {parsed_data.get('due_date')}")
            print(f"      - Line Items Found: {len(parsed_data.get('line_items', []))}")
            print(f"      - Tests Found: {len(parsed_data.get('tests', []))}")
            # Basic validation
            if len(parsed_data['line_items']) >= 1:
                print("      ✅ Correctly extracted Line Items.")
            else:
                print("      ❌ Failed to extract Line Items.")
        else:
            print("   ❌ Parsing Failed (Returned None)")

        # ---------------------------------------------------------
        # 2. Verify Proposal Drafting (MainAgent)
        # ---------------------------------------------------------
        print("\n🧪 2. Testing Proposal Drafting...")
        
        # We need data to feed the drafter. Let's use the matches from RFP-002
        rfp = db.execute(select(models.RFP).where(models.RFP.external_id == "RFP-002")).scalar_one_or_none()
        if not rfp:
            print("   ❌ RFP-002 not found! Cannot test proposal drafting.")
            return

        # Re-run matching logic to get tables
        tech_agent = TechnicalAgent()
        pricing_agent = PricingAgent()
        
        tech_table = tech_agent.process_rfp(db, rfp)
        pricing_table = pricing_agent.price_rfp(db, tech_table, rfp.tests)
        
        rfp_summary = RFPSummary(
            id=rfp.external_id,
            title=rfp.title,
            source_url=rfp.source_url,
            due_date=rfp.due_date,
            days_to_due=30,
            short_scope_summary="Cable supply"
        )

        print("   Thinking (Drafting email)...")
        proposal_text = main_agent._draft_proposal_text(rfp_summary, tech_table, pricing_table)
        
        if proposal_text and len(proposal_text) > 50:
            print("   ✅ Proposal Drafting Successful!")
            print("   📜 Preview:")
            print("-" * 40)
            print(proposal_text[:300].replace("\n", "\n      "))
            print("..." + "-" * 40)
        else:
           print("   ❌ Proposal Drafting Failed (Empty or too short)")

    except Exception as e:
        print(f"❌ Error during AI verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_ai_workflows()
