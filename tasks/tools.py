from django.db.models import Count
from tasks.models import Task

TOOLS = [
    {
        "name": "list_tasks",
        "description": "Returns all tasks ordered by priority (high to low) then creation date.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_task",
        "description": "Returns a single task by ID with full details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "The task ID"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "task_summary",
        "description": "Returns task counts grouped by status.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "high_priority_tasks",
        "description": "Returns high-priority tasks (priority=3) that are not yet done.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_tasks",
        "description": "Searches tasks by title (case-insensitive).",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "filter_tasks_by_status",
        "description": "Returns all tasks with the given status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
            },
            "required": ["status"],
        },
    },
    {
        "name": "filter_tasks_by_priority",
        "description": "Returns all tasks with the given priority. 1=Low, 2=Medium, 3=High.",
        "input_schema": {
            "type": "object",
            "properties": {
                "priority": {"type": "integer", "enum": [1, 2, 3]},
            },
            "required": ["priority"],
        },
    },
    {
        "name": "create_task",
        "description": "Creates a new task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {"type": "integer", "enum": [1, 2, 3], "default": 1},
                "description": {"type": "string", "default": ""},
                "status": {"type": "string", "enum": ["todo", "doing", "done"], "default": "todo"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "update_task",
        "description": "Updates the title and/or description of a task by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "title": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "update_task_status",
        "description": "Updates the status of a task by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "status": {"type": "string", "enum": ["todo", "doing", "done"]},
            },
            "required": ["task_id", "status"],
        },
    },
    {
        "name": "update_task_priority",
        "description": "Updates the priority of a task by ID. 1=Low, 2=Medium, 3=High.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "priority": {"type": "integer", "enum": [1, 2, 3]},
            },
            "required": ["task_id", "priority"],
        },
    },
    {
        "name": "delete_task",
        "description": "Deletes a task by ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
            },
            "required": ["task_id"],
        },
    },
]


def execute_tool(name, inputs):
    if name == "list_tasks":
        tasks = Task.objects.all()
        return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]

    elif name == "get_task":
        t = Task.objects.get(id=inputs["task_id"])
        return {"id": t.id, "title": t.title, "description": t.description, "status": t.status, "priority": t.priority, "created_at": t.created_at.isoformat(), "updated_at": t.updated_at.isoformat()}

    elif name == "task_summary":
        rows = Task.objects.values("status").annotate(count=Count("id"))
        return {row["status"]: row["count"] for row in rows}

    elif name == "high_priority_tasks":
        tasks = Task.objects.filter(priority=3).exclude(status="done")
        return [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]

    elif name == "search_tasks":
        tasks = Task.objects.filter(title__icontains=inputs["query"])
        return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]

    elif name == "filter_tasks_by_status":
        tasks = Task.objects.filter(status=inputs["status"])
        return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]

    elif name == "filter_tasks_by_priority":
        tasks = Task.objects.filter(priority=inputs["priority"])
        return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority} for t in tasks]

    elif name == "create_task":
        t = Task.objects.create(
            title=inputs["title"],
            description=inputs.get("description", ""),
            priority=inputs.get("priority", 1),
            status=inputs.get("status", "todo"),
        )
        return {"id": t.id, "title": t.title, "status": t.status, "priority": t.priority}

    elif name == "update_task":
        t = Task.objects.get(id=inputs["task_id"])
        if "title" in inputs:
            t.title = inputs["title"]
        if "description" in inputs:
            t.description = inputs["description"]
        t.save()
        return {"id": t.id, "title": t.title, "description": t.description}

    elif name == "update_task_status":
        t = Task.objects.get(id=inputs["task_id"])
        t.status = inputs["status"]
        t.save()
        return {"id": t.id, "title": t.title, "status": t.status}

    elif name == "update_task_priority":
        t = Task.objects.get(id=inputs["task_id"])
        t.priority = inputs["priority"]
        t.save()
        return {"id": t.id, "title": t.title, "priority": t.priority}

    elif name == "delete_task":
        t = Task.objects.get(id=inputs["task_id"])
        title = t.title
        t.delete()
        return {"deleted": True, "id": inputs["task_id"], "title": title}

    raise ValueError(f"Unknown tool: {name}")
