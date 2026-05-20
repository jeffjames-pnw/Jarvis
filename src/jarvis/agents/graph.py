from typing import Annotated

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from jarvis.agents.nodes import call_model


class State(TypedDict):
    messages: Annotated[list, add_messages]


_builder = StateGraph(State)
_builder.add_node("call_model", call_model)
_builder.add_edge(START, "call_model")
_builder.add_edge("call_model", END)

graph = _builder.compile()
