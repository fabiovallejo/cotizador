from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import run_chat
from app.core.dependencies import get_tenant_db, CurrentUser, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

security = HTTPBearer()

@router.post("/", response_model=ChatResponse, status_code=200, summary="Chat con la IA")
async def chat(
    data: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    response = await run_chat(
        data.message,
        current_user.usuario_id,
        current_user.empresa_id,
        current_user.db_schema, 
        data.history, 
        token=credentials.credentials,
    )
    return ChatResponse(message=response)

