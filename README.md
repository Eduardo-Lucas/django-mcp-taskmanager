# django-mcp-taskmanager

A Django-based task manager that exposes its data to AI agents via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), using [FastMCP](https://gofastmcp.com) over Streamable HTTP.

## Overview

This project demonstrates how to embed an MCP server inside a Django application using ASGI. Claude (or any MCP-compatible client) can query task data in real time through two built-in tools.

## Stack

| Layer | Technology |
|---|---|
| Web framework | Django 5.x |
| ASGI server | Uvicorn 0.49 |
| MCP server | FastMCP 3.4.2 |
| MCP transport | Streamable HTTP (stateless) |
| Database | SQLite (dev) |

## MCP Tools

| Tool | Description |
|---|---|
| `task_summary` | Returns task counts grouped by status |
| `high_priority_tasks` | Returns high-priority tasks that are not yet done |
| `create_task` | Creates a new task with title, priority, description, and status |
| `get_task` | Returns a single task by ID with full details |
| `search_tasks` | Searches tasks by title (case-insensitive) |
| `list_tasks` | Returns all tasks ordered by priority then creation date |
| `update_task` | Updates the title and/or description of a task by ID |
| `update_task_status` | Updates the status of a task by ID (todo, doing, done) |
| `update_task_priority` | Updates the priority of a task by ID (1=Low, 2=Medium, 3=High) |
| `delete_task` | Deletes a task by ID |

## Data Model

```
Task
├── title        CharField(200)
├── description  TextField
├── status       todo | doing | done
├── priority     1 (Low) | 2 (Medium) | 3 (High)
├── created_at   DateTimeField
└── updated_at   DateTimeField
```

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/Eduardo-Lucas/django-mcp-taskmanager.git
cd django-mcp-taskmanager
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run migrations

```bash
python manage.py migrate
```

### 3. Start the server

```bash
uvicorn taskmanager.asgi:application --port 8000
```

The MCP endpoint is available at `http://localhost:8000/mcp`.

## Connecting to Claude

### Claude Code (CLI)

```bash
claude mcp add taskmanager --transport http http://localhost:8000/mcp
```

Then start a new Claude Code session — the tools load automatically.

### Claude.ai (browser)

Expose the local server with ngrok:

```bash
ngrok http 8000
```

Then go to **claude.ai → Settings → Integrations** and add the ngrok HTTPS URL + `/mcp`.

> Requires a Claude Pro plan.

## Architecture

Requests are routed by a custom ASGI dispatcher in `taskmanager/asgi.py`:

```
Request
├── /mcp  →  FastMCP (stateless Streamable HTTP)
└── /*    →  Django
```

This avoids Starlette 1.x's `Mount` trailing-slash requirement by matching paths directly in the ASGI layer.

## Project Structure

```
taskmanager/
├── taskmanager/
│   ├── asgi.py       # ASGI router: FastMCP + Django
│   ├── settings.py
│   └── urls.py
└── tasks/
    ├── models.py     # Task model
    ├── mcp.py        # MCP tool definitions
    └── views.py
```
