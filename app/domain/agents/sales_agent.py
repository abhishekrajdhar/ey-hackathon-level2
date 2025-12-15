from typing import List
from datetime import date
from sqlalchemy.orm import Session
import json
import logging

from app.db import repositories, models as db_models
from app.models.schemas import RFPSummary
from app.domain.llm import generate_text
from app.services.scraper_service import GenericPSUScraper
from app.services.pdf_parser import PDFParser

logger = logging.getLogger(__name__)

class SalesAgent:
    """Identifies RFPs and prepares summaries."""

    def __init__(self):
        self.scraper = GenericPSUScraper()
    
    def scan_rfps(
        self, db: Session, urls: List[str], within_months: int = 3, live_mode: bool = False
    ) -> List[RFPSummary]:
        
        if live_mode:
            logger.info("Running in LIVE MODE: Scraping portals...")
            self._scrape_and_ingest(db, urls)
        
        # Whether live or not, we read the refined data from DB
        rfps = repositories.get_rfps_due_within(db, urls, within_months)
        
        # Pre-fetch product specs for alignment check
        all_products = repositories.get_all_products(db)
        # Create a set of (conductor, insulation) tuples for fast lookup
        inventory_specs = {
            (p.conductor.lower(), p.insulation.lower()) 
            for p in all_products 
            if p.conductor and p.insulation
        }

        results: List[RFPSummary] = []

        for rfp in rfps:
            days_to_due = (rfp.due_date - date.today()).days
            
            # --- Scoring Logic ---
            # 1. Product Alignment (Weight 0.6)
            total_lines = len(rfp.line_items)
            matched_lines = 0
            if total_lines > 0:
                for li in rfp.line_items:
                    key = (li.conductor.lower(), li.insulation.lower())
                    if key in inventory_specs:
                        matched_lines += 1
                prod_score = (matched_lines / total_lines) * 100.0
            else:
                prod_score = 0.0
            
            # 2. Time Readiness (Weight 0.4)
            # Logic: < 7 days = 0, peaks at 30 days
            if days_to_due < 7:
                time_score = 0.0
            else:
                time_score = min(100.0, (days_to_due / 30.0) * 100.0)

            final_score = (0.6 * prod_score) + (0.4 * time_score)
            
            short_scope = ", ".join(li.description for li in rfp.line_items)

            results.append(
                RFPSummary(
                    id=rfp.external_id,
                    title=rfp.title,
                    source_url=rfp.source_url,
                    due_date=rfp.due_date,
                    days_to_due=days_to_due,
                    short_scope_summary=short_scope[:200],
                    score=round(final_score, 2),
                    product_alignment_score=round(prod_score, 2),
                    time_readiness_score=round(time_score, 2),
                )
            )

        # Sort by Final Score Descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def _scrape_and_ingest(self, db: Session, urls: List[str]):
        """
        Scrapes listings, downloads PDFs, and attempts to parse/insert them into DB.
        """
        for url in urls:
            listings = self.scraper.scrape_listings(url)
            for item in listings:
                # Check if exists
                existing = repositories.get_rfp_by_external_id(db, item["title"]) # Using title as ID proxy for now
                if existing:
                    continue
                
                doc_text = ""
                if item.get("doc_url"):
                    local_path = self.scraper.download_file(item["doc_url"])
                    if local_path:
                        doc_text = PDFParser.extract_text(local_path)
                
                # Use LLM to structure this mess
                structured_data = self._llm_parse_rfp(item["title"], doc_text)
                
                if structured_data:
                    self._save_to_db(db, url, item, structured_data)

    def _llm_parse_rfp(self, title: str, text: str) -> dict | None:
        """
        Asks LLM to convert raw text -> JSON structure matching our DB models.
        """
        prompt = f"""
        You are a data extraction assistant.
        Extract structured RFP data from the following text derived from a tender document.
        
        RFP Title: {title}
        Raw Text Context:
        {text[:8000]}  # Truncate to fit context window

        Return specific JSON ONLY with this structure:
        {{
            "due_date": "YYYY-MM-DD",
            "line_items": [
                {{
                    "line_no": 1,
                    "description": "...",
                    "quantity_m": 1000,
                    "conductor": "copper|aluminium",
                    "insulation": "XLPE|PVC",
                    "voltage_kv": 1.1,
                    "cores": 3.5,
                    "size_sqmm": 95,
                    "armoured": true|false
                }}
            ],
            "tests": ["test_code_1", "test_code_2"]
        }}
        If date is missing, guess a date 30 days from now.
        """
        try:
            response_text = generate_text(prompt)
            # Sanitization in case LLM is chatty
            json_str = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None

    def _save_to_db(self, db: Session, source_url: str, listing_item: dict, data: dict):
        try:
            rfp = db_models.RFP(
                external_id=listing_item["title"][:50], # simple hack for ID
                title=listing_item["title"],
                source_url=source_url,
                due_date=date.fromisoformat(data["due_date"]),
            )
            db.add(rfp)
            db.flush() # get ID

            for item in data.get("line_items", []):
                line = db_models.RFPLineItem(
                    rfp_id=rfp.id,
                    line_no=item.get("line_no", 1),
                    description=item.get("description", "Unknown"),
                    quantity_m=float(item.get("quantity_m", 0)),
                    conductor=item.get("conductor", "copper"),
                    insulation=item.get("insulation", "XLPE"),
                    voltage_kv=float(item.get("voltage_kv", 1.1)),
                    cores=float(item.get("cores", 4)),
                    size_sqmm=float(item.get("size_sqmm", 16)),
                    armoured=bool(item.get("armoured", True)),
                )
                db.add(line)
            
            for t_code in data.get("tests", []):
                test = db_models.RFPTest(rfp_id=rfp.id, test_code=t_code)
                db.add(test)
            
            db.commit()
            logger.info(f"Ingested RFP: {rfp.title}")
            
        except Exception as e:
            logger.error(f"DB Save failed: {e}")
            db.rollback()

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
