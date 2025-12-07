from typing import List
from app.data.pricing import SKU_UNIT_PRICE, TEST_PRICE
from app.models.schemas import LineItemMatch, PricingRow, PricingSummary


class PricingAgent:
    """Assigns prices to selected SKUs and tests, consolidates totals."""

    def price_line_item(
        self,
        line_match: LineItemMatch,
        tests: List[str],
    ) -> PricingRow:
        sku = line_match.selected_sku.sku
        qty = line_match.quantity_m
        unit_price = SKU_UNIT_PRICE.get(sku, 0.0)
        material_cost = unit_price * qty

        tests_cost = sum(TEST_PRICE.get(t, 0.0) for t in tests)
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
        technical_table: List[LineItemMatch],
        tests: List[str],
    ) -> PricingSummary:
        rows: List[PricingRow] = []
        total_material = 0.0
        total_tests = 0.0

        for line in technical_table:
            row = self.price_line_item(line, tests)
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
