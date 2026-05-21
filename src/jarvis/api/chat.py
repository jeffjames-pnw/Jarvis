from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from jarvis.agents.graph import graph
from jarvis.core.auth import require_api_key

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(require_api_key)])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = await graph.ainvoke({"messages": [HumanMessage(content=request.message)]})
    content = result["messages"][-1].content
    if isinstance(content, list):
        content = "".join(block.get("text", "") for block in content if isinstance(block, dict))
    return ChatResponse(reply=content)
