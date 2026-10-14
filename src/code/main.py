import logging
import os
import sys
from mcp.server import MCPServer

from odoo_client import OdooClient
from crm import CRMModule
from products import ProductsModule
from inventory import InventoryModule
from projects import ProjectsModule
from sales import SalesModule

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = MCPServer("odoo-server")

ODOO_SERVER = os.environ.get("ODOO_SERVER")
ODOO_DB = os.environ.get("ODOO_DB")
ODOO_USER = os.environ.get("ODOO_USER")
ODOO_API_KEY = os.environ.get("ODOO_API_KEY")

client = OdooClient(
    url=ODOO_SERVER,
    db=ODOO_DB,
    username=ODOO_USER,
    api_key=ODOO_API_KEY
)

crm_module = CRMModule(client)
products_module = ProductsModule(client)
inventory_module = InventoryModule(client)
projects_module = ProjectsModule(client)
sales_module = SalesModule(client)

sales_module.register_tools(mcp)
crm_module.register_tools(mcp)
products_module.register_tools(mcp)
inventory_module.register_tools(mcp)
projects_module.register_tools(mcp)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
