# microfinance_backend/asgi.py

import os
from django.core.asgi import get_asgi_application
# Import the function that provides the application instance
from apps.telegram.apps import get_telegram_application
import logging
# from django.conf import settings # Import settings within the lifespan event for safety

logger = logging.getLogger(__name__)

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'microfinance_backend.settings')

# Get the standard Django ASGI application (this is what handles your Django views)
django_asgi_app = get_asgi_application()

# Define the custom ASGI application entry point that includes lifespan handling
async def application(scope, receive, send):
    # Handle lifespan events (startup, shutdown)
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                logger.info("ASGI Lifespan startup event received.")
                # Ensure Django settings are loaded here, especially for WEBHOOK_URL
                from django.conf import settings

                print(f"--- DEBUG ASGI: Attempting to get Telegram Application instance... ---")
                telegram_bot_application = get_telegram_application() # Get the instance (builds if first time)

                print(f"--- DEBUG ASGI: telegram_bot_application after get_telegram_application() call: {telegram_bot_application is None} ---")
                print(f"--- DEBUG ASGI: settings.BOT_TOKEN is set: {bool(getattr(settings, 'BOT_TOKEN', None))} ---")
                print(f"--- DEBUG ASGI: settings.WEBHOOK_URL is set: {bool(getattr(settings, 'WEBHOOK_URL', None))} ---")


                if telegram_bot_application and settings.BOT_TOKEN and settings.WEBHOOK_URL:
                    logger.info(f"Telegram BOT_TOKEN and WEBHOOK_URL ({settings.WEBHOOK_URL}) are set. Attempting bot initialization.")
                    try:
                        # Initialize the PTB Application in the async context
                        await telegram_bot_application.initialize(webhook_url=settings.WEBHOOK_URL)
                        logger.info("Telegram bot Application initialized via ASGI lifespan startup successfully.")
                        print(f"--- DEBUG: Application initialized via ASGI. Is _initialized: {telegram_bot_application._initialized} ---")
                        # Signal Uvicorn that startup is complete
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as e:
                        logger.error(f"Error initializing Telegram bot Application during ASGI startup: {e}", exc_info=True)
                        # Signal Uvicorn that startup failed
                        await send({"type": "lifespan.startup.failed", "message": f"Bot initialization failed: {e}"})
                else:
                    logger.warning("Telegram bot Application instance is None or BOT_TOKEN/WEBHOOK_URL not set. Skipping bot initialization during ASGI startup.")
                    print("--- DEBUG ASGI: Skipping bot initialization due to condition not met. ---")
                    # Allow app to start even if bot initialization is skipped/fails
                    await send({"type": "lifespan.startup.complete"})
            elif message['type'] == 'lifespan.shutdown':
                logger.info("ASGI Lifespan shutdown event received.")
                # Optional: Perform any cleanup here if needed, e.g., deleting webhook
                # On shutdown, you might want to call get_telegram_application() again to get the instance
                # if it was initialized, and then call its cleanup methods.
                # await telegram_bot_application.bot.delete_webhook() # Example: delete webhook on shutdown
                await send({"type": "lifespan.shutdown.complete"})
                return # Exit the lifespan loop
    else:
        # For all other scopes (e.g., 'http', 'websocket'), pass control to Django's ASGI app
        await django_asgi_app(scope, receive, send)