from pydantic import BaseModel
from typing import List, Dict
from datetime import date


class RFPSummary(BaseModel):
    id: str
    title: str
    source_url: str
    due_date: date
    days_to_due: int
    short_scope_summary: str


class SpecMatchEntry(BaseModel):
    sku: str
    name: str
    spec_match_percent: float
    specs: Dict[str, str]


class LineItemMatch(BaseModel):
    line_id: int
    description: str
    quantity_m: float
    top_3_matches: List[SpecMatchEntry]
    selected_sku: SpecMatchEntry


class PricingRow(BaseModel):
    line_id: int
    selected_sku: str
    quantity_m: float
    unit_price: float
    material_cost: float
    tests_cost: float
    total_cost: float


class PricingSummary(BaseModel):
    currency: str = "INR"
    rows: List[PricingRow]
    total_material_cost: float
    total_tests_cost: float
    grand_total: float


class FullRFPResponse(BaseModel):
    rfp_summary: RFPSummary
    technical_table: List[LineItemMatch]
    pricing_table: PricingSummary
