from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []

class ChatResponse(BaseModel):
    message: str


#Luego se puede modificar para que en el schema se puedan devolver pdf de cotizaciones