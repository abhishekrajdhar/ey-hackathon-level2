from typing import List
from datetime import date
from sqlalchemy.orm import Session

from app.db import repositories
from app.models.schemas import RFPSummary
from app.domain.llm import generate_text


class SalesAgent:
    """Identifies RFPs and prepares summaries."""

    def scan_rfps(
        self, db: Session, urls: List[str], within_months: int = 3
    ) -> List[RFPSummary]:
        rfps = repositories.get_rfps_due_within(db, urls, within_months)
        results: List[RFPSummary] = []

        for rfp in rfps:
            days_to_due = (rfp.due_date - date.today()).days
            short_scope = ", ".join(li.description for li in rfp.line_items)

            results.append(
                RFPSummary(
                    id=rfp.external_id,
                    title=rfp.title,
                    source_url=rfp.source_url,
                    due_date=rfp.due_date,
                    days_to_due=days_to_due,
                    short_scope_summary=short_scope[:200],
                )
            )

        results.sort(key=lambda r: r.due_date)
        return results

    def choose_rfp_for_response(self, rfps: List[RFPSummary]) -> RFPSummary | None:
        return rfps[0] if rfps else None

    def summarize_for_roles(self, rfp) -> dict[str, str]:
        """
        Uses Gemini to create role-specific summaries from the RFP object.
        """
        base_text = "\n".join(
            f"Line {li.line_no}: {li.description}, qty={li.quantity_m} m"
            for li in rfp.line_items
        )
        tests_text = ", ".join(t.test_code for t in rfp.tests)

        technical_prompt = f"""
You are a cable design engineer.

RFP scope:
{base_text}

Summarize ONLY the technical scope of supply in bullet points.
"""
        pricing_prompt = f"""
You are a pricing analyst.

RFP tests and acceptance requirements:
{tests_text}

Summarize the tests and any cost drivers in 5 bullets.
"""
        management_prompt = f"""
You are a sales manager.

RFP title: {rfp.title}
Due date: {rfp.due_date}

Write a crisp 3-line business summary focusing on opportunity size and urgency.
"""

        return {
            "technical_summary": generate_text(technical_prompt),
            "pricing_summary": generate_text(pricing_prompt),
            "management_summary": generate_text(management_prompt),
        }
