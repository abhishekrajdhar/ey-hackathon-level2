
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db import models

def verify_data():
    db = SessionLocal()
    try:
        print("🔍 Verifying Data Insertion...")
        
        # Check Products
        products = db.scalars(select(models.Product)).all()
        print(f"\n📊 Total Products: {len(products)}")
        for p in products:
            print(f"   - {p.sku}: {p.name} ({p.category})")

        # Check RFPs
        rfps = db.scalars(select(models.RFP)).all()
        print(f"\n📑 Total RFPs: {len(rfps)}")
        for r in rfps:
            print(f"   - {r.external_id}: {r.title} ({len(r.line_items)} items, {len(r.tests)} tests)")

        # Check Prices
        sku_prices = db.scalars(select(models.SkuPrice)).all()
        print(f"\n💰 Total SKU Prices: {len(sku_prices)}")
        
        test_prices = db.scalars(select(models.TestPrice)).all()
        print(f"💰 Total Test Prices: {len(test_prices)}")

    finally:
        db.close()

if __name__ == "__main__":
    verify_data()
