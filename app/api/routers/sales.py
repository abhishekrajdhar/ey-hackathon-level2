from typing import List
from fastapi import APIRouter, Depends, Query
from app.domain.agents.sales_agent import SalesAgent
from app.models.schemas import RFPSummary

router = APIRouter(prefix="/sales", tags=["sales"])


def get_sales_agent() -> SalesAgent:
    return SalesAgent()


@router.get("/scan", response_model=List[RFPSummary])
def scan_rfps(
    urls: List[str] = Query(
        default=[
            "https://example-lstk1.com/tenders",
            "https://example-lstk2.com/rfps",
        ],
        description="List of URLs for Sales Agent to scan",
    ),
    months: int = 3,
    agent: SalesAgent = Depends(get_sales_agent),
):
    """
    Sales Agent:
    - Scans given URLs
    - Returns RFPs due in the next `months` months.
    """
    return agent.scan_rfps(urls, within_months=months)
