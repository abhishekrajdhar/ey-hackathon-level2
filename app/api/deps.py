from app.domain.agents.main_agent import MainAgent


def get_main_agent() -> MainAgent:
    # Could be enhanced with DI container / lifecycle mgmt
    return MainAgent()
