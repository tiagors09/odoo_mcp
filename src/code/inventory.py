from typing import Any, Dict, List, Optional, Annotated
from pydantic import Field
import asyncio
from odoo_client import OdooClient

class InventoryModule:
    """Handles inventory stock quants and stock levels."""

    def __init__(self, client: OdooClient):
        self.client = client
        self.model = "stock.quant"

    def get_stock_levels(self, domain: Optional[List[Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Check available quantities per product across locations."""
        domain = domain or []
        fields = ["product_id", "quantity", "location_id", "reserved_quantity"]
        return self.client.execute(self.model, "search_read", [domain], {"fields": fields, "limit": limit})

    def register_tools(self, mcp_server) -> None:
        """Register inventory tools into the MCP server."""

        @mcp_server.tool(
            name="get_stock_levels",
            title="Get Stock Levels",
            description="Check available quantities per product and reserved quantities across locations in Odoo inventory.",
        )
        async def get_stock_levels(
            limit: Annotated[
                int, Field(description="Maximum number of inventory records to return (default 50)")
            ] = 50,
        ) -> str:
            """Tool wrapper to check stock levels."""
            try:
                levels = await asyncio.to_thread(
                    self.get_stock_levels,
                    domain=None,
                    limit=limit
                )

                if not levels:
                    return "No stock levels found."

                return str(levels)

            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"
