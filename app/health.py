"""Health check endpoint for monitoring."""

import logging

from aiohttp import web
from airtable.kek_storage import kek_storage

logger = logging.getLogger(__name__)


async def health_check(request):
    """
    Health check endpoint for monitoring.

    Checks:
    - Airtable connectivity by fetching keks

    Returns:
        200 OK if healthy
        503 Service Unavailable if unhealthy
    """
    try:
        # Try to fetch keks to verify Airtable connectivity
        keks = await kek_storage.async_all()

        if keks is None:
            logger.error("Health check failed: keks is None")
            return web.Response(text="ERROR: No data from storage", status=503)

        return web.Response(
            text=f"OK - {len(keks)} keks available",
            status=200,
            content_type="text/plain",
        )

    except TimeoutError:
        logger.error("Health check failed: Airtable timeout")
        return web.Response(
            text="ERROR: Storage timeout", status=503, content_type="text/plain"
        )
    except Exception as e:
        logger.exception("Health check failed with unexpected error")
        return web.Response(
            text=f"ERROR: {str(e)}", status=503, content_type="text/plain"
        )


async def start_health_check_server(port: int = 8080):
    """
    Start the health check HTTP server.

    Args:
        port: Port to listen on (default: 8080)

    Returns:
        aiohttp.web.AppRunner instance
    """
    app = web.Application()
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)  # Also respond on root

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Health check server started on port {port}")

    return runner
