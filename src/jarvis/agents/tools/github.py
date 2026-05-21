import json
import logging

from github import Github, GithubException
from langchain_core.tools import tool

from jarvis.core.config import settings

logger = logging.getLogger(__name__)


def _client() -> Github:
    return Github(settings.github_token) if settings.github_token else Github()


@tool
def list_my_issues() -> str:
    """List open GitHub issues assigned to me across all my repositories."""
    try:
        g = _client()
        user = g.get_user()
        issues = g.search_issues(f"assignee:{user.login} is:open is:issue")
        results = [
            {
                "repo": i.repository.full_name,
                "title": i.title,
                "url": i.html_url,
                "labels": [label.name for label in i.labels],
            }
            for i in list(issues[:20])
        ]
        return json.dumps(results, indent=2) if results else "No open issues assigned to you."
    except GithubException as e:
        return f"GitHub error: {e}"


@tool
def list_my_prs() -> str:
    """List open pull requests I created or that are awaiting my review."""
    try:
        g = _client()
        user = g.get_user()
        authored = g.search_issues(f"author:{user.login} is:open is:pr")
        review_requested = g.search_issues(f"review-requested:{user.login} is:open is:pr")
        results = {
            "authored": [
                {"repo": p.repository.full_name, "title": p.title, "url": p.html_url}
                for p in list(authored[:10])
            ],
            "review_requested": [
                {"repo": p.repository.full_name, "title": p.title, "url": p.html_url}
                for p in list(review_requested[:10])
            ],
        }
        return json.dumps(results, indent=2)
    except GithubException as e:
        return f"GitHub error: {e}"


@tool
def search_code(query: str, repo: str = "") -> str:
    """Search code in my GitHub repositories.

    Args:
        query: The code search query.
        repo: Optional specific repo to search in, e.g. 'username/reponame'.
    """
    try:
        g = _client()
        user = g.get_user()
        qualified = f"{query} user:{user.login}"
        if repo:
            qualified = f"{query} repo:{repo}"
        results_raw = g.search_code(qualified)
        results = [
            {"repo": r.repository.full_name, "path": r.path, "url": r.html_url}
            for r in list(results_raw[:10])
        ]
        return json.dumps(results, indent=2) if results else "No matching code found."
    except GithubException as e:
        return f"GitHub error: {e}"


@tool
def get_my_activity() -> str:
    """Get my recent GitHub activity — commits, PRs opened, issues commented on."""
    try:
        g = _client()
        user = g.get_user()
        own_events = [
            e for e in user.get_events()
            if e.repo.name.split("/")[0] == user.login
        ][:20]
        results = [
            {"type": e.type, "repo": e.repo.name, "created_at": e.created_at.isoformat()}
            for e in own_events
        ]
        return json.dumps(results, indent=2) if results else "No recent activity found."
    except GithubException as e:
        return f"GitHub error: {e}"
