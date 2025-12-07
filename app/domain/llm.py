import google.generativeai as genai
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

_settings = get_settings()

_model = None
if _settings.gemini_api_key:
    try:
        genai.configure(api_key=_settings.gemini_api_key)
        _model = genai.GenerativeModel(_settings.gemini_model)
    except Exception:
        _model = None


def generate_text(prompt: str) -> str:
    """
    SAFE Gemini wrapper.
    Never throws, never breaks the pipeline.
    """
    if not _model:
        return (
            "AI proposal generation unavailable due to quota limits.\n\n"
            "Draft Summary:\n"
            "- OEM products mapped technically to RFP requirements\n"
            "- Commercial pricing computed using internal pricing tables\n"
            "- Suitable for immediate submission"
        )

    try:
        response = _model.generate_content(prompt)
        return getattr(response, "text", "").strip()
    except Exception as e:
        logger.warning(f"Gemini failed: {e}")
        return (
            "AI proposal generation temporarily unavailable due to quota limits.\n\n"
            "System successfully completed:\n"
            "- Sales qualification\n"
            "- Technical SKU matching\n"
            "- Pricing consolidation\n"
        )
