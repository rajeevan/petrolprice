"""
Petrol Price add-on: load config, run HTTP server (ingress), and periodically
fetch image -> OCR -> parse -> store for API.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

from aiohttp import web

from api_server import create_app, set_prices
from ocr_parser import fetch_and_parse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

OPTIONS_PATH = Path("/data/options.json")
DEFAULT_SCAN_HOURS = 6.0
DEFAULT_PORT = 8099


def load_config() -> dict:
    if not OPTIONS_PATH.exists():
        raise FileNotFoundError(f"Options not found: {OPTIONS_PATH}")
    with open(OPTIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    url = data.get("image_url") or ""
    if not url:
        raise ValueError("image_url is required in add-on options")
    hours = float(data.get("scan_interval_hours") or DEFAULT_SCAN_HOURS)
    return {"image_url": url, "scan_interval_hours": hours}


def run_parse(image_url: str) -> list[dict]:
    """Synchronous fetch+parse; run in executor to not block event loop."""
    try:
        return fetch_and_parse(image_url)
    except Exception as e:
        logger.exception("Parse failed")
        return []


async def fetch_loop(config: dict) -> None:
    image_url = config["image_url"]
    interval_seconds = max(60, config["scan_interval_hours"] * 3600)
    loop = asyncio.get_event_loop()

    while True:
        logger.info("Fetching and parsing image...")
        try:
            prices = await loop.run_in_executor(None, run_parse, image_url)
            if prices:
                set_prices(prices, error=None)
                logger.info("Parsed %d fuel types", len(prices))
            else:
                set_prices([], error="No fuel prices parsed")
        except Exception as e:
            logger.exception("Fetch/parse error")
            set_prices([], error=str(e))
        await asyncio.sleep(interval_seconds)


async def start_background_tasks(app: web.Application) -> None:
    config = app["config"]
    asyncio.create_task(fetch_loop(config))


def main() -> None:
    config = load_config()
    app = create_app()
    app["config"] = config
    app.on_startup.append(start_background_tasks)

    # Run one parse immediately so API has data soon
    try:
        initial = run_parse(config["image_url"])
        set_prices(initial, error=None)
        if initial:
            logger.info("Initial parse: %d fuel types", len(initial))
    except Exception as e:
        logger.warning("Initial parse failed: %s", e)
        set_prices([], error=str(e))

    logger.info("Starting HTTP server on port %s", DEFAULT_PORT)
    web.run_app(app, host="0.0.0.0", port=DEFAULT_PORT)


if __name__ == "__main__":
    main()
