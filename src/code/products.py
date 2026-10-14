from typing import Any, Dict, List, Optional, Annotated
from pydantic import Field
import asyncio
from odoo_client import OdooClient

class ProductsModule:
    """Handles product catalog operations."""

    def __init__(self, client: OdooClient):
        self.client = client
        self.model = "product.template"

    def search_products(self, domain: Optional[List[Any]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search products and return their name, price, and stock info."""
        domain = domain or []
        fields = ["name", "list_price", "qty_available", "default_code"]
        return self.client.execute(self.model, "search_read", [domain], {"fields": fields, "limit": limit})

    def register_tools(self, mcp_server) -> None:
        """Register product tools into the MCP server."""

        @mcp_server.tool(
            name="search_products",
            title="Search Products",
            description="Search products in Odoo catalog, returning name, price, available quantity, and internal reference code.",
        )
        async def search_products(
            limit: Annotated[
                int, Field(description="Maximum number of products to return (default 20)")
            ] = 20,
        ) -> str:
            """Tool wrapper to search products."""
            try:
                products = await asyncio.to_thread(
                    self.search_products,
                    domain=None,
                    limit=limit
                )

                if not products:
                    return "No products found."

                return str(products)

            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"
