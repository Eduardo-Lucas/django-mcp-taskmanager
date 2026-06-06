from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Import the MCP toolset to register it with the global server
        import tasks.mcp # noqa - triggers toolset + tools registration
