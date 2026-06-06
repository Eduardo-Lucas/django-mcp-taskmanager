import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
django.setup()

from django.core.asgi import get_asgi_application
from fastmcp import FastMCP

mcp = FastMCP("Task Manager")

@mcp.tool()
def task_summary() -> dict:
    """Returns task counts grouped by status."""
    from django.db.models import Count
    from tasks.models import Task
    rows = Task.objects.values("status").annotate(count=Count("id"))
    return {row["status"]: row["count"] for row in rows}

@mcp.tool()
def high_priority_tasks() -> list:
    """Returns high-priority tasks that are not yet done."""
    from tasks.models import Task
    tasks = Task.objects.filter(priority=3).exclude(status="done")
    return [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]

mcp_app = mcp.http_app(path="/mcp", stateless_http=True)
django_app = get_asgi_application()

async def application(scope, receive, send):
    # Route lifespan to mcp_app so the session manager starts/stops correctly.
    # Route /mcp (and /mcp/*) to FastMCP; everything else to Django.
    if scope["type"] == "lifespan" or scope.get("path", "").startswith("/mcp"):
        await mcp_app(scope, receive, send)
    else:
        await django_app(scope, receive, send)
