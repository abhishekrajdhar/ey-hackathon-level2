from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models

def seed_db():
    db: Session = SessionLocal()

    try:
        # -------------------------------
        # Products
        # -------------------------------
        products = [
            models.Product(
                sku="AP-CABLE-001",
                name="AP Copper XLPE 1.1kV 4C 16sqmm",
                category="Power Cable",
                conductor="copper",
                insulation="XLPE",
                voltage_kv=1.1,
                cores=4,
                size_sqmm=16,
                application="feeder",
                armoured=True,
            ),
            models.Product(
                sku="AP-CABLE-002",
                name="AP Copper PVC 1.1kV 2C 4sqmm",
                category="Control Cable",
                conductor="copper",
                insulation="PVC",
                voltage_kv=1.1,
                cores=2,
                size_sqmm=4,
                application="control",
                armoured=False,
            ),
        ]
        db.add_all(products)

        # -------------------------------
        # SKU Prices
        # -------------------------------
        db.add_all([
            models.SkuPrice(sku="AP-CABLE-001", unit_price=150.0),
            models.SkuPrice(sku="AP-CABLE-002", unit_price=75.0),
        ])

        # -------------------------------
        # Test Prices
        # -------------------------------
        db.add_all([
            models.TestPrice(test_code="routine_electrical_tests", price=5000.0),
            models.TestPrice(test_code="insulation_resistance_test", price=6000.0),
        ])

        # -------------------------------
        # RFP
        # -------------------------------
        rfp = models.RFP(
            external_id="RFP-001",
            title="Supply of LV Cables for Metro Depot",
            source_url="https://example-lstk1.com/tenders",
            due_date=date.today() + timedelta(days=45),
        )
        db.add(rfp)
        db.flush()  # get rfp.id

        # -------------------------------
        # RFP Line Items
        # -------------------------------
        db.add_all([
            models.RFPLineItem(
                rfp_id=rfp.id,
                line_no=1,
                description="4C 16sqmm Cu XLPE 1.1kV armoured feeder cable",
                quantity_m=5000,
                conductor="copper",
                insulation="XLPE",
                voltage_kv=1.1,
                cores=4,
                size_sqmm=16,
                armoured=True,
            ),
            models.RFPLineItem(
                rfp_id=rfp.id,
                line_no=2,
                description="2C 4sqmm Cu PVC 1.1kV control cable",
                quantity_m=3000,
                conductor="copper",
                insulation="PVC",
                voltage_kv=1.1,
                cores=2,
                size_sqmm=4,
                armoured=False,
            ),
        ])

        # -------------------------------
        # RFP Tests
        # -------------------------------
        db.add_all([
            models.RFPTest(rfp_id=rfp.id, test_code="routine_electrical_tests"),
            models.RFPTest(rfp_id=rfp.id, test_code="insulation_resistance_test"),
        ])

        db.commit()
        print("✅ Database seeded successfully")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
