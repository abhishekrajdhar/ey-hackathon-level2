from typing import Dict, List
from sqlalchemy.orm import Session

from app.db import repositories
from app.domain.spec_matching import compute_spec_match
from app.models.schemas import SpecMatchEntry, LineItemMatch
from app.db import models as db_models


class TechnicalAgent:
    """Matches RFP line items with OEM SKUs using DB data."""

    def _build_product_specs(self, products: list[db_models.Product]) -> list[dict]:
        return [
            {
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "specs": {
                    "conductor": p.conductor,
                    "insulation": p.insulation,
                    "voltage_kV": p.voltage_kv,
                    "cores": p.cores,
                    "size_sqmm": p.size_sqmm,
                    "application": p.application,
                    "armoured": p.armoured,
                },
            }
            for p in products
        ]

    def match_line_item(
        self,
        db: Session,
        line_item: db_models.RFPLineItem,
        products: list[dict],
    ) -> LineItemMatch:
        required_specs = {
            "conductor": line_item.conductor,
            "insulation": line_item.insulation,
            "voltage_kV": line_item.voltage_kv,
            "cores": line_item.cores,
            "size_sqmm": line_item.size_sqmm,
            "armoured": line_item.armoured,
        }

        scored: List[SpecMatchEntry] = []
        for prod in products:
            score = compute_spec_match(required_specs, prod["specs"])
            scored.append(
                SpecMatchEntry(
                    sku=prod["sku"],
                    name=prod["name"],
                    spec_match_percent=score,
                    specs={k: str(v) for k, v in prod["specs"].items()},
                )
            )

        scored.sort(key=lambda x: x.spec_match_percent, reverse=True)
        top3 = scored[:3]
        selected = top3[0] if top3 else None

        return LineItemMatch(
            line_id=line_item.line_no,
            description=line_item.description,
            quantity_m=line_item.quantity_m,
            top_3_matches=top3,
            selected_sku=selected,
        )

    def process_rfp(self, db: Session, rfp: db_models.RFP) -> List[LineItemMatch]:
        products = self._build_product_specs(repositories.get_all_products(db))
        return [self.match_line_item(db, li, products) for li in rfp.line_items]
