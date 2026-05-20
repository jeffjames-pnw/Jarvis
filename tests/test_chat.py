from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage

from jarvis.main import app


@pytest.mark.asyncio
async def test_chat_returns_reply():
    mock_result = {"messages": [AIMessage(content="Hello! How can I help you today?")]}
    with patch("jarvis.api.chat.graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=mock_result)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/chat", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"reply": "Hello! How can I help you today?"}


@pytest.mark.asyncio
async def test_chat_passes_message_to_graph():
    mock_result = {"messages": [AIMessage(content="Sure!")]}
    with patch("jarvis.api.chat.graph") as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value=mock_result)
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/chat", json={"message": "do something"})
        call_args = mock_graph.ainvoke.call_args[0][0]
    assert call_args["messages"][0].content == "do something"
