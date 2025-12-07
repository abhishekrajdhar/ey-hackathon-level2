from typing import List
from sqlalchemy.orm import Session

from app.db import repositories
from app.db import models as db_models
from app.models.schemas import LineItemMatch, PricingRow, PricingSummary


class PricingAgent:
    """Assigns prices to selected SKUs and tests, using DB tables."""

    def price_line_item(
        self,
        db: Session,
        line_match: LineItemMatch,
        tests: list[db_models.RFPTest],
    ) -> PricingRow:
        sku = line_match.selected_sku.sku
        qty = line_match.quantity_m

        unit_price = repositories.get_sku_price(db, sku)
        material_cost = unit_price * qty

        test_codes = [t.test_code for t in tests]
        test_price_map = repositories.get_test_prices(db, test_codes)
        tests_cost = sum(test_price_map.get(code, 0.0) for code in test_codes)

        total_cost = material_cost + tests_cost

        return PricingRow(
            line_id=line_match.line_id,
            selected_sku=sku,
            quantity_m=qty,
            unit_price=unit_price,
            material_cost=round(material_cost, 2),
            tests_cost=round(tests_cost, 2),
            total_cost=round(total_cost, 2),
        )

    def price_rfp(
        self,
        db: Session,
        technical_table: List[LineItemMatch],
        tests: list[db_models.RFPTest],
    ) -> PricingSummary:
        rows: List[PricingRow] = []
        total_material = 0.0
        total_tests = 0.0

        for line in technical_table:
            row = self.price_line_item(db, line, tests)
            rows.append(row)
            total_material += row.material_cost
            total_tests += row.tests_cost

        grand = total_material + total_tests

        return PricingSummary(
            rows=rows,
            total_material_cost=round(total_material, 2),
            total_tests_cost=round(total_tests, 2),
            grand_total=round(grand, 2),
        )
