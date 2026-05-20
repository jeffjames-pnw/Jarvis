from jarvis.core.llm import get_llm


def call_model(state: dict) -> dict:
    response = get_llm().invoke(state["messages"])
    return {"messages": [response]}
