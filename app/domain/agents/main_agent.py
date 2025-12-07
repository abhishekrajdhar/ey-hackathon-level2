from typing import List, Dict, Optional
from fastapi import HTTPException
from app.data.rfp_listings import RFP_LISTINGS
from app.domain.agents.sales_agent import SalesAgent
from app.domain.agents.technical_agent import TechnicalAgent
from app.domain.agents.pricing_agent import PricingAgent
from app.models.schemas import FullRFPResponse, LineItemMatch, RFPSummary, PricingSummary


class MainAgent:
    """
    Orchestrator:
    - uses SalesAgent to find & choose RFP
    - uses TechnicalAgent for SKU matching & spec tables
    - uses PricingAgent for consolidated prices
    """

    def __init__(self) -> None:
        self.sales = SalesAgent()
        self.tech = TechnicalAgent()
        self.pricing = PricingAgent()

    @staticmethod
    def _get_rfp_by_id(rfp_id: str) -> Optional[Dict]:
        for r in RFP_LISTINGS:
            if r["id"] == rfp_id:
                return r
        return None

    def run_full_pipeline(self, urls: List[str]) -> FullRFPResponse:
        # 1) Sales Agent: scan + choose RFP
        candidates: List[RFPSummary] = self.sales.scan_rfps(urls)
        chosen = self.sales.choose_rfp_for_response(candidates)
        if not chosen:
            raise HTTPException(status_code=404, detail="No qualifying RFPs found.")

        raw_rfp = self._get_rfp_by_id(chosen.id)
        if not raw_rfp:
            raise HTTPException(status_code=500, detail="Selected RFP not found.")

        # 2) Technical Agent
        tech_table: List[LineItemMatch] = self.tech.process_rfp(raw_rfp)

        # 3) Pricing Agent
        pricing_table: PricingSummary = self.pricing.price_rfp(
            tech_table, raw_rfp["tests_and_acceptance"]
        )

        # 4) Consolidated response
        return FullRFPResponse(
            rfp_summary=chosen,
            technical_table=tech_table,
            pricing_table=pricing_table,
        )
