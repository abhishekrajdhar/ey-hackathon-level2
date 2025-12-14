from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db import repositories, models as db_models
from app.domain.agents.sales_agent import SalesAgent
from app.domain.agents.technical_agent import TechnicalAgent
from app.domain.agents.pricing_agent import PricingAgent
from app.domain.llm import generate_text
from app.models.schemas import FullRFPResponse, RFPSummary, LineItemMatch, PricingSummary


class MainAgent:
    """
    Orchestrator:
    - SalesAgent: identify RFP
    - TechnicalAgent: spec match
    - PricingAgent: costing
    - LLM: final narrative proposal
    """

    def __init__(self) -> None:
        self.sales = SalesAgent()
        self.tech = TechnicalAgent()
        self.pricing = PricingAgent()

    def run_full_pipeline(self, db: Session, urls: List[str], live_mode: bool = False) -> FullRFPResponse:
        # 1) Sales Agent
        candidates: List[RFPSummary] = self.sales.scan_rfps(db, urls, live_mode=live_mode)
        chosen = self.sales.choose_rfp_for_response(candidates)
        if not chosen:
            raise HTTPException(status_code=404, detail="No qualifying RFPs found.")

        rfp: db_models.RFP | None = repositories.get_rfp_by_external_id(
            db, chosen.id
        )
        if not rfp:
            raise HTTPException(status_code=500, detail="Selected RFP not found.")

        # 2) Technical
        technical_table: List[LineItemMatch] = self.tech.process_rfp(db, rfp)

        # 3) Pricing
        pricing_table: PricingSummary = self.pricing.price_rfp(db, technical_table, rfp.tests)

        # 4) (Optional) LLM-generated textual proposal (not in schema, but you can add)
        proposal_text = self._draft_proposal_text(chosen, technical_table, pricing_table)

        # You can attach proposal_text somewhere (e.g. extend FullRFPResponse)
        # For now you can log or return alongside.
        # Example: add `proposal_text: str` field in FullRFPResponse.

        return FullRFPResponse(
            rfp_summary=chosen,
            technical_table=technical_table,
            pricing_table=pricing_table,
        )

    def _draft_proposal_text(
        self,
        rfp_summary: RFPSummary,
        technical_table: List[LineItemMatch],
        pricing: PricingSummary,
    ) -> str:
        items_txt = "\n".join(
            f"- Line {li.line_id}: {li.selected_sku.name} ({li.selected_sku.sku}), "
            f"qty={li.quantity_m} m, spec_match={li.selected_sku.spec_match_percent}%"
            for li in technical_table
        )

        pricing_txt = (
            f"Total material cost: INR {pricing.total_material_cost:.2f}\n"
            f"Total test cost: INR {pricing.total_tests_cost:.2f}\n"
            f"Grand total: INR {pricing.grand_total:.2f}"
        )

        prompt = f"""
You are a B2B sales engineer at an industrial cables OEM.

Create a professional RFP response email.

RFP:
- Title: {rfp_summary.title}
- Due date: {rfp_summary.due_date}
- Scope lines and selected products:
{items_txt}

Pricing:
{pricing_txt}

Write:
- A short intro
- A bullet list of key technical offerings
- A bullet list of commercial highlights
- A polite closing.

Keep it concise and business-like.
"""
        return generate_text(prompt)
