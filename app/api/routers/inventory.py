from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db
from app.db import repositories
from app.models.schemas import ProductCreate, PriceUpdate

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.post("/products", status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a new product in the catalog.
    If 'unit_price' is provided (>0), it also sets the price.
    """
    try:
        # Pydantic -> Dict
        data = product.model_dump()
        new_prod = repositories.create_product(db, data)
        return {
            "msg": "Product created successfully",
            "sku": new_prod.sku,
            "id": new_prod.id
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="SKU already exists.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prices")
def update_price(price_update: PriceUpdate, db: Session = Depends(get_db)):
    """
    Updates or sets the price for a given SKU.
    """
    try:
        updated = repositories.update_sku_price(db, price_update.sku, price_update.unit_price)
        db.commit()
        return {"msg": "Price updated", "sku": updated.sku, "unit_price": updated.unit_price}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
