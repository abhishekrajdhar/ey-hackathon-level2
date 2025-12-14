from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta
from typing import List

from app.db import models
from app.data.rfp_listings import TODAY  # or compute date.today()

def get_rfps_due_within(
    db: Session, urls: List[str], months: int
) -> list[models.RFP]:
    cutoff = TODAY + timedelta(days=months * 30)
    stmt = (
        select(models.RFP)
        .where(models.RFP.source_url.in_(urls))
        .where(models.RFP.due_date <= cutoff)
    )
    return list(db.scalars(stmt))


def get_rfp_by_external_id(db: Session, external_id: str) -> models.RFP | None:
    stmt = select(models.RFP).where(models.RFP.external_id == external_id)
    return db.scalars(stmt).first()


def get_all_products(db: Session) -> list[models.Product]:
    stmt = select(models.Product)
    return list(db.scalars(stmt))


def get_sku_price(db: Session, sku: str) -> float:
    stmt = select(models.SkuPrice).where(models.SkuPrice.sku == sku)
    row = db.scalars(stmt).first()
    return row.unit_price if row else 0.0


def get_test_prices(db: Session, codes: list[str]) -> dict[str, float]:
    if not codes:
        return {}
    stmt = select(models.TestPrice).where(models.TestPrice.test_code.in_(codes))
    rows = db.scalars(stmt).all()
    return {r.test_code: r.price for r in rows}


def create_product(db: Session, product_data: dict) -> models.Product:
    # 1. Create Product
    product = models.Product(
        sku=product_data["sku"],
        name=product_data["name"],
        category=product_data["category"],
        conductor=product_data["conductor"],
        insulation=product_data["insulation"],
        voltage_kv=product_data["voltage_kv"],
        cores=product_data["cores"],
        size_sqmm=product_data["size_sqmm"],
        application=product_data["application"],
        armoured=product_data["armoured"],
    )
    db.add(product)
    
    # 2. Set Price if provided
    if product_data.get("unit_price", 0) > 0:
        update_sku_price(db, product_data["sku"], product_data["unit_price"])
        
    db.commit()
    db.refresh(product)
    return product


def update_sku_price(db: Session, sku: str, price: float) -> models.SkuPrice:
    stmt = select(models.SkuPrice).where(models.SkuPrice.sku == sku)
    existing = db.scalars(stmt).first()
    
    if existing:
        existing.unit_price = price
        db.add(existing)
        return existing
    else:
        new_price = models.SkuPrice(sku=sku, unit_price=price)
        db.add(new_price)
        return new_price
