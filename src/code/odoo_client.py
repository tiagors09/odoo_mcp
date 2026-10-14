import httpx
from typing import Any, Dict, List, Optional

class OdooClient:
    """Base client to handle JSON-RPC communication with Odoo using httpx."""

    def __init__(self, url: str, db: str, username: str, api_key: str):
        self.url = url.rstrip("/") + "/jsonrpc"
        self.db = db
        self.username = username
        self.api_key = api_key
        self.uid: Optional[int] = None

    def authenticate(self) -> int:
        """Authenticate user against Odoo common service and store the UID."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.username, self.api_key, {}]
            },
            "id": 1
        }

        with httpx.Client() as client:
            response = client.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            raise RuntimeError(f"Odoo Authentication Failed: {data['error']}")

        self.uid = data.get("result")
        if not self.uid:
            raise ValueError("Authentication returned a false/empty UID. Check credentials.")

        return self.uid

    def execute(self, model: str, method: str, args: List[Any], kwargs: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a model method (execute_kw) via JSON-RPC object service."""
        if not self.uid:
            self.authenticate()

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db,
                    self.uid,
                    self.api_key,
                    model,
                    method,
                    args,
                    kwargs or {}
                ]
            },
            "id": 2
        }

        with httpx.Client() as client:
            response = client.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        if "error" in data:
            raise RuntimeError(f"Odoo Execution Error [{model}.{method}]: {data['error']}")

        return data.get("result")
