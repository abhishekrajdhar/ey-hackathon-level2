from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.domain.agents.sales_agent import SalesAgent
from app.db.session import get_db
from app.models.schemas import RFPSummary

router = APIRouter(prefix="/sales", tags=["sales"])


def get_sales_agent() -> SalesAgent:
    return SalesAgent()


@router.get("/scan", response_model=List[RFPSummary])
def scan_rfps(
    urls: List[str] = Query(
        default=[
            "http://test.com",
        ],
        description="List of URLs for Sales Agent to scan",
    ),
    months: int = 3,
    db: Session = Depends(get_db),
    agent: SalesAgent = Depends(get_sales_agent),
):
    return agent.scan_rfps(db, urls, within_months=months)
