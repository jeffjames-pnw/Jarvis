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
    # this runs the graph initialized above
    # loading the llm within the call_model in nodes.py
    result = await graph.ainvoke({"messages": [HumanMessage(content=request.message)]})
    return ChatResponse(reply=result["messages"][-1].content)
