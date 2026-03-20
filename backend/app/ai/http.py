from httpx import AsyncClient, ASGITransport
from app.main import app

def get_internal_client(token: str) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://internal",
        headers={"Authorization": f"Bearer {token}"},
    )