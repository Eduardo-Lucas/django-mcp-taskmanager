from django.db.models import QuerySet
from mcp_server.djangomcp import global_mcp_server
from mcp_server.query_tool import ModelQueryToolset
from .models import Task

class TaskToolset(ModelQueryToolset):
    """Exposes the Task model to AI agents."""
    model = Task

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by('-priority', '-created_at')
    
    
@global_mcp_server.tool()
def task_summary() -> dict:
    """Returns task counts grouped by status."""
    from django.db.models import Count
    rows = Task.objects.values("status").annotate(count=Count("id"))
    return {row["status"]: row["count"] for row in rows}


@global_mcp_server.tool()
def high_priority_tasks() -> list:
    """Returns high-priority tasks that are not yet done."""
    tasks = Task.objects.filter(priority=3).exclude(status="done")
    return [
        {"id": t.id, "title": t.title, "status": t.status}
        for t in tasks
    ]
