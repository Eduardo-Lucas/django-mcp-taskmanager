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

@mcp.tool()
def list_tasks() -> list:
    """Returns all tasks ordered by priority (high to low) then creation date."""
    from tasks.models import Task
    return [
        {"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "description": t.description}
        for t in Task.objects.all()
    ]

@mcp.tool()
def delete_task(task_id: int) -> dict:
    """Deletes a task by ID. Returns the deleted task's title and id."""
    from tasks.models import Task
    task = Task.objects.get(id=task_id)
    title = task.title
    task.delete()
    return {"deleted": True, "id": task_id, "title": title}

@mcp.tool()
def update_task_status(task_id: int, status: str) -> dict:
    """Updates the status of a task. status: todo, doing, done."""
    from tasks.models import Task
    if status not in ("todo", "doing", "done"):
        raise ValueError("status must be todo, doing, or done")
    task = Task.objects.get(id=task_id)
    task.status = status
    task.save()
    return {"id": task.id, "title": task.title, "status": task.status}

@mcp.tool()
def create_task(title: str, priority: int = 1, description: str = "", status: str = "todo") -> dict:
    """Creates a new task. priority: 1=Low, 2=Medium, 3=High. status: todo, doing, done."""
    from tasks.models import Task
    if priority not in (1, 2, 3):
        raise ValueError("priority must be 1, 2, or 3")
    if status not in ("todo", "doing", "done"):
        raise ValueError("status must be todo, doing, or done")
    task = Task.objects.create(title=title, description=description, priority=priority, status=status)
    return {"id": task.id, "title": task.title, "status": task.status, "priority": task.priority}

mcp_app = mcp.http_app(path="/mcp", stateless_http=True)
django_app = get_asgi_application()

async def application(scope, receive, send):
    # Route lifespan to mcp_app so the session manager starts/stops correctly.
    # Route /mcp (and /mcp/*) to FastMCP; everything else to Django.
    if scope["type"] == "lifespan" or scope.get("path", "").startswith("/mcp"):
        await mcp_app(scope, receive, send)
    else:
        await django_app(scope, receive, send)
