from typing import List
from datetime import date, timedelta
from app.data.rfp_listings import RFP_LISTINGS, TODAY
from app.models.schemas import RFPSummary


class SalesAgent:
    """Identifies RFPs from URLs and summarizes them."""

    def scan_rfps(self, urls: List[str], within_months: int = 3) -> List[RFPSummary]:
        cutoff_date = TODAY + timedelta(days=within_months * 30)
        results: List[RFPSummary] = []

        for rfp in RFP_LISTINGS:
            if rfp["source_url"] not in urls:
                continue
            if rfp["due_date"] > cutoff_date:
                continue

            days_to_due = (rfp["due_date"] - TODAY).days
            short_scope = ", ".join(li["description"] for li in rfp["scope_of_supply"])

            results.append(
                RFPSummary(
                    id=rfp["id"],
                    title=rfp["title"],
                    source_url=rfp["source_url"],
                    due_date=rfp["due_date"],
                    days_to_due=days_to_due,
                    short_scope_summary=short_scope[:200],
                )
            )

        results.sort(key=lambda r: r.due_date)
        return results

    def choose_rfp_for_response(self, rfps: List[RFPSummary]) -> RFPSummary | None:
        return rfps[0] if rfps else None
