from typing import List
from fastapi import APIRouter, Depends, Query
from app.api.deps import get_main_agent
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
    main_agent: MainAgent = Depends(get_main_agent),
):
    """
    Main Agent:
    - Uses Sales Agent to identify an RFP due within next 3 months.
    - Uses Technical Agent to match SKUs and compute spec match %.
    - Uses Pricing Agent to estimate costs.
    - Returns consolidated technical + pricing response for that RFP.
    """
    return main_agent.run_full_pipeline(urls)
