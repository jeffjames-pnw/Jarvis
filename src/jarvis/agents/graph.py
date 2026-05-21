from langgraph.prebuilt import create_react_agent

from jarvis.agents.tools.github import get_my_activity, list_my_issues, list_my_prs, search_code
from jarvis.agents.tools.notes import search_notes
from jarvis.core.llm import get_llm

_SYSTEM_PROMPT = """You are Jarvis, a personal assistant with access to Jeff's GitHub and notes.

When answering questions:
- Use the available tools to look up current information rather than guessing.
- For GitHub questions, use the appropriate tool (issues, PRs, code search, or activity).
- For questions about notes or personal knowledge, use search_notes.
- Be concise and direct. Cite sources (repo names, note titles) in your answers.
- If a tool returns no results, say so honestly rather than making something up.
"""

tools = [list_my_issues, list_my_prs, search_code, get_my_activity, search_notes]

graph = create_react_agent(get_llm(), tools=tools, prompt=_SYSTEM_PROMPT)
