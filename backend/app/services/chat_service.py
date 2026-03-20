from agents import Runner
from app.ai.agent import agent
from app.ai.context import ChatContext


async def run_chat(message: str, user_id: int, company_id: int, db_schema: str, history: list[dict[str, str]], token: str) -> str:
    # Construir contexto del tenant para las tools
    context = ChatContext(db_schema=db_schema, user_id=user_id, company_id=company_id, token=token)

    # Construir contexto del historial
    history_text = ""
    if history:
        history_text = "\n".join(
            f"{'Usuario' if h.get('role') == 'user' else 'Asistente'}: {h.get('content', '')}"
            for h in history
        )
        history_text = f"\nHistorial de conversación:\n{history_text}\n"

    input_text = f"""{history_text}
Usuario dijo: {message}
user_id: {user_id}
company_id: {company_id}
"""
    result = await Runner.run(agent, input=input_text, context=context)
    return result.final_output
