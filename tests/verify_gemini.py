
from app.db.session import SessionLocal
from app.db import models
from app.domain.agents.sales_agent import SalesAgent
from app.domain.llm import generate_text
from sqlalchemy import select
import os

def test_gemini_integration():
    print("🤖 Verifying Gemini Integration...")
    
    # 1. Check API Key presence
    api_key = os.getenv("GEMINI_API_KEY") # This might not be loaded if not in .env or exported
    print(f"   🔑 GEMINI_API_KEY env var present: {bool(api_key)}")

    # 2. Test generate_text directly
    print("\n   🧪 Testing generate_text('Hello, do you exist?')...")
    response = generate_text("Hello, do you exist?")
    
    print(f"   📜 Response: {response[:100]}...")
    
    if "AI proposal generation unavailable" in response:
        print("   ⚠️  FALLBACK DETECTED: Not using real Gemini API.")
    else:
        print("   ✅ SUCCESS: Received response from Gemini (or at least not fallback).")

    # 3. Test SalesAgent summarization
    print("\n   🧪 Testing SalesAgent.summarize_for_roles...")
    db = SessionLocal()
    try:
        rfp = db.execute(select(models.RFP).where(models.RFP.external_id == "RFP-002")).scalar_one_or_none()
        if rfp:
            agent = SalesAgent()
            summaries = agent.summarize_for_roles(rfp)
            print("   📊 Summaries Generated:")
            for role, text in summaries.items():
                print(f"      - {role}: {text[:50]}...")
                if "AI proposal generation unavailable" in text:
                     print(f"        ⚠️  {role} summary is using FALLBACK.")
                else:
                     print(f"        ✅ {role} summary seems REAL.")
        else:
            print("   ❌ RFP-002 not found for context test.")
    finally:
        db.close()

if __name__ == "__main__":
    test_gemini_integration()
