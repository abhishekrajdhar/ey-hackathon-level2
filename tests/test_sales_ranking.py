from datetime import date, timedelta
from app.domain.agents.sales_agent import SalesAgent
from app.db import models
from app.db.session import engine
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup in-memory DB for testing
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_sales_ranking_logic():
    db = TestSessionLocal()
    sales_agent = SalesAgent()

    try:
        # 1. Clear existing data to avoid noise
        db.query(models.RFPTest).delete()
        db.query(models.RFPLineItem).delete()
        db.query(models.RFP).delete()
        db.query(models.Product).delete()
        db.commit()

        # 2. Seed Products (Conductor/Insulation keys)
        prod = models.Product(
            sku="TEST-SKU-1", name="Test Cable", category="Power",
            conductor="copper", insulation="xlpe", # Lowercase for match
            voltage_kv=1.1, cores=4, size_sqmm=16, application="test", armoured=True
        )
        db.add(prod)
        db.commit()

        # 3. Seed RFPs
        
        # RFP A: 2 days due (Too soon), 100% match
        rfp_a = models.RFP(
            external_id="RFP-A", title="Urgent Match", source_url="http://test.com",
            due_date=date.today() + timedelta(days=2)
        )
        db.add(rfp_a)
        db.flush()
        db.add(models.RFPLineItem(rfp_id=rfp_a.id, line_no=1, description="Match", conductor="copper", insulation="xlpe", quantity_m=100, voltage_kv=1.1, cores=4, size_sqmm=16, armoured=True))
        
        # RFP B: 20 days due (Good time), 100% match
        rfp_b = models.RFP(
            external_id="RFP-B", title="Standard Match", source_url="http://test.com",
            due_date=date.today() + timedelta(days=20)
        )
        db.add(rfp_b)
        db.flush()
        db.add(models.RFPLineItem(rfp_id=rfp_b.id, line_no=1, description="Match", conductor="copper", insulation="xlpe", quantity_m=100, voltage_kv=1.1, cores=4, size_sqmm=16, armoured=True))

        # RFP C: 45 days due (Best time), 100% match
        rfp_c = models.RFP(
            external_id="RFP-C", title="Long Match", source_url="http://test.com",
            due_date=date.today() + timedelta(days=45)
        )
        db.add(rfp_c)
        db.flush()
        db.add(models.RFPLineItem(rfp_id=rfp_c.id, line_no=1, description="Match", conductor="copper", insulation="xlpe", quantity_m=100, voltage_kv=1.1, cores=4, size_sqmm=16, armoured=True))

        # RFP D: 45 days due (Best time), 0% match
        rfp_d = models.RFP(
            external_id="RFP-D", title="Long No Match", source_url="http://test.com",
            due_date=date.today() + timedelta(days=45)
        )
        db.add(rfp_d)
        db.flush()
        db.add(models.RFPLineItem(rfp_id=rfp_d.id, line_no=1, description="No Match", conductor="gold", insulation="paper", quantity_m=100, voltage_kv=1.1, cores=4, size_sqmm=16, armoured=True))

        db.commit()

        # 4. Run Scan
        results = sales_agent.scan_rfps(db, urls=["http://test.com"], within_months=3)
        
        print("\n--- Ranking Results ---")
        for i, r in enumerate(results):
            print(f"{i+1}. {r.id} | Score: {r.score} (Prod: {r.product_alignment_score}, Time: {r.time_readiness_score})")

        # 5. Assertions
        # Expect Order: C > B > A > D
        # Logic Check:
        # C: Prod 100, Time 100 -> 60 + 40 = 100
        # B: Prod 100, Time ~66 -> 60 + 26.6 = ~86.6
        # A: Prod 100, Time 0 (<7 days) -> 60 + 0 = 60
        # D: Prod 0, Time 100 -> 0 + 40 = 40

        assert results[0].id == "RFP-C", f"Expected RFP-C first, got {results[0].id}"
        assert results[1].id == "RFP-B", f"Expected RFP-B second, got {results[1].id}"
        assert results[2].id == "RFP-A", f"Expected RFP-A third, got {results[2].id}"
        assert results[3].id == "RFP-D", f"Expected RFP-D last, got {results[3].id}"

        print("\n✅ Test Passed: Smart Ranking Logic is Correct.")

    finally:
        db.close()

if __name__ == "__main__":
    test_sales_ranking_logic()


