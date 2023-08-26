import logging
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(filename="startup.log")
logger.addHandler(file_handler)

try:
    import fastapi
    import os

    from fastapi.middleware import cors
    from rest import controllers

except (ImportError, ModuleNotFoundError) as err:
    logger.error({'msg': err})
    raise SystemExit(
        "Some of the modules failed to be loaded, check logs for more information"
    )

# Environment Variables

DEBUG_MODE = os.environ.get("DEBUG_MODE", False)
VERSION = os.environ.get("VERSION", "1.0.0")

# CORS configuration
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*")
ALLOWED_HEADERS = os.environ.get("ALLOWED_HEADERS", "*")

application = fastapi.FastAPI(
    debug=DEBUG_MODE,
    version=VERSION
)

try:
    # Adding Middlewares

    application.add_middleware(
        middleware_class=cors.CORSMiddleware,
        allow_origins=[
            host for host in ALLOWED_HOSTS] if ALLOWED_HOSTS else ["*"],
        allow_headers=[
            header for header in ALLOWED_HEADERS] if ALLOWED_HEADERS else ["*"],
        allow_methods=["POST", "OPTIONS", "GET"]
    )

    # Adding Rest Endpoints

    application.add_api_route(
        path='/healthcheck/',
        methods=['GET'],
        endpoint=controllers.healthcheck,
        description="Standard Heathcheck REST Endpoint"
    )

    application.add_api_route(
        path='/api/analyze/',
        methods=['POST'],
        endpoint=controllers.analyze_social_media_acrhive,
        description='Analyzes given screenshot files'
    )

except (fastapi.exceptions.FastAPIError, AttributeError, IndexError) as err:
    logger.critical(err)
    raise SystemExit(
        "Failed to start application, check logs"
    )