"""
HTTP server for ingress: GET /api/prices returns JSON list of {fuel_type, price}.
Data is read from the shared cache updated by main loop.
"""
import json
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

# Module-level cache; updated by main.py
_prices_cache: list[dict] = []
_error_message: str | None = None


def set_prices(data: list[dict], error: str | None = None) -> None:
    global _prices_cache, _error_message
    _prices_cache = data if data is not None else []
    _error_message = error


async def handle_prices(_request: web.Request) -> web.Response:
    """GET /api/prices -> JSON list of {fuel_type, price}."""
    global _prices_cache, _error_message
    if _error_message:
        return web.json_response(
            {"error": _error_message, "prices": _prices_cache},
            status=200,
        )
    return web.json_response({"prices": _prices_cache})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/api/prices", handle_prices)
    return app
