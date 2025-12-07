from app.domain.agents.main_agent import MainAgent
from app.db.session import get_db 


def get_main_agent() -> MainAgent:
    # Could be enhanced with DI container / lifecycle mgmt
    return MainAgent()
