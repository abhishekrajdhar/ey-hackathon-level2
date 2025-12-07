from typing import Dict, List
from app.data.products import PRODUCT_SPECS
from app.domain.spec_matching import compute_spec_match
from app.models.schemas import SpecMatchEntry, LineItemMatch


class TechnicalAgent:
    """Matches RFP line items with OEM SKUs and prepares spec tables."""

    def match_line_item(self, line_item: Dict) -> LineItemMatch:
        required_specs = line_item["required_specs"]
        quantity = line_item["quantity_m"]
        description = line_item["description"]

        scored_candidates: List[SpecMatchEntry] = []
        for prod in PRODUCT_SPECS:
            score = compute_spec_match(required_specs, prod["specs"])
            scored_candidates.append(
                SpecMatchEntry(
                    sku=prod["sku"],
                    name=prod["name"],
                    spec_match_percent=score,
                    specs={k: str(v) for k, v in prod["specs"].items()},
                )
            )

        scored_candidates.sort(key=lambda x: x.spec_match_percent, reverse=True)
        top3 = scored_candidates[:3]
        selected = top3[0] if top3 else None

        return LineItemMatch(
            line_id=line_item["line_id"],
            description=description,
            quantity_m=quantity,
            top_3_matches=top3,
            selected_sku=selected,
        )

    def process_rfp(self, rfp: Dict) -> List[LineItemMatch]:
        return [self.match_line_item(li) for li in rfp["scope_of_supply"]]
