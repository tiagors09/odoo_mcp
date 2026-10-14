from typing import Any, Dict, List, Optional, Annotated
from pydantic import Field
import asyncio
from odoo_client import OdooClient

class SalesModule:
    """Handles sales quotations and orders."""

    def __init__(self, client: OdooClient):
        self.client = client
        self.model = "sale.order"

    def create_quotation(self, partner_id: int, order_lines: List[Dict[str, Any]]) -> int:
        """Create a new sale quotation/order with lines."""
        formatted_lines = [[0, 0, line] for line in order_lines]
        vals = {
            "partner_id": partner_id,
            "order_line": formatted_lines
        }
        return self.client.execute(self.model, "create", [vals])

    def get_orders(self, domain: Optional[List[Any]] = None, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Fetch sale orders."""
        domain = domain or []
        fields = fields or ["name", "partner_id", "amount_total", "state"]
        return self.client.execute(self.model, "search_read", [domain], {"fields": fields})

    def register_tools(self, mcp_server) -> None:
        """Register sales tools into the MCP server."""

        @mcp_server.tool(
            name="create_quotation",
            title="Create Sales Quotation",
            description="Create a new sale quotation/order in Odoo with partner and order lines, returning its record ID.",
        )
        async def create_quotation(
            partner_id: Annotated[int, Field(description="ID of the customer/partner for the quotation")],
            order_lines: Annotated[
                List[Dict[str, Any]],
                Field(description="List of order lines, e.g. [{'product_id': 1, 'product_uom_qty': 2, 'price_unit': 50.0}]")
            ],
        ) -> str:
            try:
                order_id = await asyncio.to_thread(
                    self.create_quotation,
                    partner_id=partner_id,
                    order_lines=order_lines
                )
                if not order_id:
                    return "Error: Odoo did not return the created quotation ID."
                return f"Quotation successfully created! Record ID: {order_id}"
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"

        @mcp_server.tool(
            name="get_orders",
            title="Get Sales Orders",
            description="Fetch sales orders from Odoo, returning order name, partner, total amount, and state.",
        )
        async def get_orders(
            fields: Annotated[
                Optional[List[str]],
                Field(description="Optional list of fields to retrieve (e.g. ['name', 'amount_total'])")
            ] = None,
        ) -> str:
            try:
                orders = await asyncio.to_thread(
                    self.get_orders,
                    domain=None,
                    fields=fields
                )
                if not orders:
                    return "No sales orders found."
                return str(orders)
            except Exception as e:
                return f"Error communicating with Odoo server: {str(e)}"
