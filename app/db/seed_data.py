from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db import models

def get_or_create(session: Session, model, **kwargs):
    instance = session.execute(select(model).filter_by(**kwargs)).scalar_one_or_none()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.flush() # Populate ID
        return instance, True

def seed_db():
    db: Session = SessionLocal()

    try:
        print("🌱 Seeding database...")

        # -------------------------------
        # Products
        # -------------------------------
        # Define product data
        product_data_list = [
             # Existing Copper
            {
                "sku": "AP-CABLE-001",
                "name": "AP Copper XLPE 1.1kV 4C 16sqmm",
                "category": "Power Cable",
                "conductor": "copper",
                "insulation": "XLPE",
                "voltage_kv": 1.1,
                "cores": 4,
                "size_sqmm": 16,
                "application": "feeder",
                "armoured": True,
            },
            {
                "sku": "AP-CABLE-002",
                "name": "AP Copper PVC 1.1kV 2C 4sqmm",
                "category": "Control Cable",
                "conductor": "copper",
                "insulation": "PVC",
                "voltage_kv": 1.1,
                "cores": 2,
                "size_sqmm": 4,
                "application": "control",
                "armoured": False,
            },
             # New Aluminum
            {
                "sku": "AP-CABLE-003",
                "name": "AP Aluminum XLPE 1.1kV 3.5C 185sqmm",
                "category": "Power Cable",
                "conductor": "aluminum",
                "insulation": "XLPE",
                "voltage_kv": 1.1,
                "cores": 3.5,
                "size_sqmm": 185,
                "application": "distribution",
                "armoured": True,
            },
            {
                "sku": "AP-CABLE-004",
                "name": "AP Aluminum PVC 1.1kV 4C 25sqmm",
                "category": "Power Cable",
                "conductor": "aluminum",
                "insulation": "PVC",
                "voltage_kv": 1.1,
                "cores": 4,
                "size_sqmm": 25,
                "application": "lighting",
                "armoured": True,
            },
            # High Voltage
            {
                "sku": "HV-CABLE-001",
                "name": "HV Copper XLPE 11kV 3C 240sqmm",
                "category": "HV Cable",
                "conductor": "copper",
                "insulation": "XLPE",
                "voltage_kv": 11.0,
                "cores": 3,
                "size_sqmm": 240,
                "application": "transmission",
                "armoured": True,
            },
        ]

        for p_data in product_data_list:
            sku = p_data.pop("sku")
            # Check by SKU
            existing = db.execute(select(models.Product).where(models.Product.sku == sku)).scalar_one_or_none()
            if not existing:
                db.add(models.Product(sku=sku, **p_data))
                print(f"   Created Product: {sku}")
            else:
                print(f"   Skipped Product: {sku} (Exists)")

        # -------------------------------
        # SKU Prices
        # -------------------------------
        sku_prices = [
            ("AP-CABLE-001", 150.0),
            ("AP-CABLE-002", 75.0),
            ("AP-CABLE-003", 420.0),
            ("AP-CABLE-004", 110.0),
            ("HV-CABLE-001", 3500.0),
        ]

        for sku, price in sku_prices:
             # Simple upsert for price
            existing_price = db.execute(select(models.SkuPrice).where(models.SkuPrice.sku == sku)).scalar_one_or_none()
            if existing_price:
                existing_price.unit_price = price
            else:
                db.add(models.SkuPrice(sku=sku, unit_price=price))

        # -------------------------------
        # Test Prices
        # -------------------------------
        test_prices = [
            ("routine_electrical_tests", 5000.0),
            ("insulation_resistance_test", 6000.0),
            ("type_test_hv", 15000.0),
            ("fire_resistance_test", 12000.0),
        ]
        for code, price in test_prices:
             existing_test = db.execute(select(models.TestPrice).where(models.TestPrice.test_code == code)).scalar_one_or_none()
             if existing_test:
                 existing_test.price = price
             else:
                 db.add(models.TestPrice(test_code=code, price=price))

        # -------------------------------
        # RFPs
        # -------------------------------
        rfps_data = [
            {
                "external_id": "RFP-001",
                "title": "Supply of LV Cables for Metro Depot",
                "source_url": "https://example-lstk1.com/tenders",
                "due_date": date.today() + timedelta(days=45),
                "items": [
                    {
                        "line_no": 1, "description": "4C 16sqmm Cu XLPE 1.1kV armoured feeder cable", "quantity_m": 5000,
                        "conductor": "copper", "insulation": "XLPE", "voltage_kv": 1.1, "cores": 4, "size_sqmm": 16, "armoured": True
                    },
                    {
                         "line_no": 2, "description": "2C 4sqmm Cu PVC 1.1kV control cable", "quantity_m": 3000,
                         "conductor": "copper", "insulation": "PVC", "voltage_kv": 1.1, "cores": 2, "size_sqmm": 4, "armoured": False
                    }
                ],
                "tests": ["routine_electrical_tests", "insulation_resistance_test"]
            },
            {
                "external_id": "RFP-002",
                "title": "Annual Cable Supply - West Zone",
                "source_url": "https://power-grid-west.com/procurement",
                "due_date": date.today() + timedelta(days=30),
                "items": [
                    {
                        "line_no": 1, "description": "3.5C 185sqmm Al XLPE 1.1kV armoured cable", "quantity_m": 12000,
                        "conductor": "aluminum", "insulation": "XLPE", "voltage_kv": 1.1, "cores": 3.5, "size_sqmm": 185, "armoured": True
                    },
                     {
                        "line_no": 2, "description": "11kV 3C 240sqmm Cu XLPE Cable", "quantity_m": 500,
                        "conductor": "copper", "insulation": "XLPE", "voltage_kv": 11.0, "cores": 3, "size_sqmm": 240, "armoured": True
                    }
                ],
                 "tests": ["routine_electrical_tests", "type_test_hv"]
            }
        ]

        for rfp_data in rfps_data:
            ext_id = rfp_data["external_id"]
            existing_rfp = db.execute(select(models.RFP).where(models.RFP.external_id == ext_id)).scalar_one_or_none()
            
            if not existing_rfp:
                print(f"   Creating RFP: {ext_id}")
                rfp = models.RFP(
                    external_id=ext_id,
                    title=rfp_data["title"],
                    source_url=rfp_data["source_url"],
                    due_date=rfp_data["due_date"]
                )
                db.add(rfp)
                db.flush() # Get ID

                # Add items
                for item in rfp_data["items"]:
                    db.add(models.RFPLineItem(rfp_id=rfp.id, **item))
                
                # Add tests
                for t_code in rfp_data["tests"]:
                    db.add(models.RFPTest(rfp_id=rfp.id, test_code=t_code))
            else:
                 print(f"   Skipped RFP: {ext_id} (Exists)")


        db.commit()
        print("✅ Database seeded successfully")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
