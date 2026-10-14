from typing import Any, Dict, List, Optional, Annotated
from pydantic import Field
import asyncio
from odoo_client import OdooClient

class ProjectsModule:
    """Handles project management and tasks."""

    def __init__(self, client: OdooClient):
        self.client = client
        self.model = "project.task"

    def create_project(self, name: str) -> int:
        pass

    def create_task(self, name: str, project_id: int, user_id: Optional[int] = None) -> int:
        """Create a new task inside a specific project."""
        vals: Dict[str, Any] = {
            "name": name,
            "project_id": project_id
        }
        if user_id:
            vals["user_ids"] = [(4, user_id)]
        return self.client.execute(self.model, "create", [vals])

    def get_tasks(self, domain: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Fetch tasks based on filter domains."""
        domain = domain or []
        fields = ["name", "project_id", "stage_id", "date_deadline"]
        return self.client.execute(self.model, "search_read", [domain], {"fields": fields})

    def register_tools(self, mcp_server) -> None:
        """Register project and task tools into the MCP server."""

        @mcp_server.tool(
            name="create_task",
            title="Create Project Task",
            description="Create a new task inside a specific project in Odoo and return its record ID.",
        )
        async def create_task(
            name: Annotated[str, Field(description="Task name (e.g. \"Setup Server\")")],
            project_id: Annotated[int, Field(description="ID of the project where the task will be created")],
            user_id: Annotated[Optional[int], Field(description="Optional user ID to assign to the task")] = None,
        ) -> str:
            try:
                task_id = await asyncio.to_thread(
                    self.create_task,
                    name=name,
                    project_id=project_id,
                    user_id=user_id
                )
                if not task_id:
                    return "Error: Odoo did not return the created task ID."
                return f"Task successfully created! Record ID: {task_id}"
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"

        @mcp_server.tool(
            name="get_tasks",
            title="Get Project Tasks",
            description="Fetch tasks from Odoo, returning their name, project, stage, and deadline.",
        )
        async def get_tasks() -> str:
            try:
                tasks = await asyncio.to_thread(
                    self.get_tasks,
                    domain=None
                )
                if not tasks:
                    return "No tasks found."
                return str(tasks)
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"
