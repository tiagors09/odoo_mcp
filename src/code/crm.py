from typing import Any, Dict, List, Annotated
from pydantic import Field
import asyncio
from odoo_client import OdooClient

class CRMModule:
    """Handles CRM operations such as leads and opportunities."""

    def __init__(self, client: OdooClient):
        self.client = client
        self.model = "crm.lead"

    def create_opportunity(self, name: str, expected_revenue: float = 0.0, priority: str = "1") -> int:
        """Create a new CRM opportunity and return its record ID."""
        vals = {
            "name": name,
            "type": "opportunity",
            "expected_revenue": expected_revenue,
            "priority": priority
        }
        return self.client.execute(self.model, "create", [vals])

    def search_opportunities(self, domain: List[Any], fields: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search and read CRM opportunities based on a domain filter."""
        return self.client.execute(self.model, "search_read", [domain], {"fields": fields, "limit": limit})

    def register_tools(self, mcp_server) -> None:
        """Register CRM tools into the MCP server."""

        @mcp_server.tool(
            name="create_opportunity",
            title="Create CRM Opportunity",
            description="Create a new CRM opportunity/lead in Odoo and return its record ID.",
        )
        async def create_opportunity(
            name: Annotated[str, Field(description="Opportunity or lead name (e.g. \"Big Market Deal\")")],
            expected_revenue: Annotated[float, Field(description="Expected revenue amount in currency (default 0.0)")] = 0.0,
            priority: Annotated[str, Field(description="Priority level: '0' (Low), '1' (Normal), '2' (High), '3' (Very High)")] = "1",
        ) -> str:
            try:
                lead_id = await asyncio.to_thread(
                    self.create_opportunity,
                    name=name,
                    expected_revenue=expected_revenue,
                    priority=priority
                )
                if not lead_id:
                    return "Error: Odoo did not return the created record ID."
                return f"Opportunity successfully created! Record ID: {lead_id}"
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"

        @mcp_server.tool(
            name="search_opportunities",
            title="Search CRM Opportunities",
            description="Search and read CRM opportunities based on Odoo domain filters.",
        )
        async def search_opportunities(
            fields: Annotated[List[str], Field(description="List of field names to retrieve (e.g. ['name', 'expected_revenue'])")],
            limit: Annotated[int, Field(description="Maximum number of records to return (default 10)")] = 10,
        ) -> str:
            try:
                domain = []
                opportunities = await asyncio.to_thread(
                    self.search_opportunities,
                    domain=domain,
                    fields=fields,
                    limit=limit
                )
                if not opportunities:
                    return "No opportunities found with the given criteria."
                return str(opportunities)
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"
