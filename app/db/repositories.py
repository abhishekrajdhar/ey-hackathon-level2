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
