from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from jarvis.agents.graph import graph

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await graph.ainvoke({"messages": [HumanMessage(content=request.message)]})
    return ChatResponse(reply=result["messages"][-1].content)
