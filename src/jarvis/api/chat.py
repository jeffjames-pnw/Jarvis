from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

# this loads agents/graph.py
# which imports call_model from agents/nodes.py
# and builds the state graph
# at startup time to initialize ahead of call time
from jarvis.agents.graph import graph

router = APIRouter(prefix="/chat", tags=["chat"])


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
