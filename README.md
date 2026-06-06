# django-mcp-taskmanager

A Django-based task manager that exposes its data to AI agents via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), using [FastMCP](https://gofastmcp.com) over Streamable HTTP. Includes a browser-based chat UI powered by Claude.

## Overview

This project demonstrates how to embed an MCP server inside a Django application using ASGI. Claude (or any MCP-compatible client) can query and manage task data in real time through a full set of tools. A built-in chat interface lets you interact with your tasks in plain English.

## Stack

| Layer | Technology |
|---|---|
| Web framework | Django 5.x |
| ASGI server | Uvicorn 0.49 |
| MCP server | FastMCP 3.4.2 |
| MCP transport | Streamable HTTP (stateless) |
| AI model | Claude claude-sonnet-4-6 (Anthropic) |
| Database | SQLite (dev) |

## MCP Tools

| Tool | Description |
|---|---|
| `list_tasks` | Returns all tasks ordered by priority then creation date |
| `get_task` | Returns a single task by ID with full details |
| `task_summary` | Returns task counts grouped by status |
| `high_priority_tasks` | Returns high-priority tasks that are not yet done |
| `filter_tasks_by_status` | Returns all tasks with a given status (todo, doing, done) |
| `filter_tasks_by_priority` | Returns all tasks with a given priority (1=Low, 2=Medium, 3=High) |
| `search_tasks` | Searches tasks by title (case-insensitive) |
| `create_task` | Creates a new task with title, priority, description, and status |
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

### 2. Configure environment

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Get your key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Create a user

```bash
python manage.py createsuperuser
```

### 5. Start the server

```bash
uvicorn taskmanager.asgi:application --port 8000
```

### 6. Open the chat UI

Go to `http://localhost:8000/chat/` — you'll be redirected to the login page. After signing in you can start managing tasks in plain English.

## Connecting to Claude Code (CLI)

```bash
claude mcp add taskmanager --transport http http://localhost:8000/mcp
```

Then start a new Claude Code session — the tools load automatically.

## Connecting to Claude.ai (browser)

Expose the local server with ngrok:

```bash
ngrok http 8000
```

Then go to **claude.ai → Settings → Integrations** and add the ngrok HTTPS URL + `/mcp`.

> Requires a Claude Pro plan.

## Architecture

```
Request
├── /mcp    →  FastMCP (stateless Streamable HTTP)
├── /chat/  →  Chat UI (Django template)
└── /*      →  Django
```

Requests are routed by a custom ASGI dispatcher in `taskmanager/asgi.py`, avoiding Starlette 1.x's `Mount` trailing-slash limitation.

The chat UI calls the Anthropic API directly from a Django view, executing tool calls against the local database and streaming responses back to the browser via SSE.

## Project Structure

```
taskmanager/
├── .env                         # ANTHROPIC_API_KEY (not committed)
├── taskmanager/
│   ├── asgi.py                  # ASGI router: FastMCP + Django
│   ├── settings.py
│   └── urls.py
└── tasks/
    ├── models.py                # Task model
    ├── tools.py                 # Tool definitions shared by chat and MCP
    ├── mcp.py                   # MCP server tool registrations
    ├── views.py                 # Chat page and API views
    └── templates/tasks/
        └── chat.html            # Chat UI
```
