from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_main_agent
from app.db.session import get_db
from app.domain.agents.main_agent import MainAgent
from app.models.schemas import FullRFPResponse

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.get("/run", response_model=FullRFPResponse)
def run_full_pipeline(
    urls: List[str] = Query(
        default=[
            "https://example-lstk1.com/tenders",
            "https://example-lstk2.com/rfps",
        ],
        description="List of URLs that may contain RFP listings.",
    ),
    db: Session = Depends(get_db),
    main_agent: MainAgent = Depends(get_main_agent),
):
    return main_agent.run_full_pipeline(db, urls)
