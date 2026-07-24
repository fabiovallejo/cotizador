from dataclasses import dataclass

@dataclass
class ChatContext:
    """Contexto del chat que se pasa a las tools del agente vía RunContext."""
    db_schema: str
    user_id: int
    company_id: int
    token: str