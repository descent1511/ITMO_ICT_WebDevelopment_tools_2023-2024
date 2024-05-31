from .celery_app import celery_app
from .utils import parse_url
from .api_client import get_user_id, update_user
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def parse_url_task(url: str):
    result = parse_url(url)
    logger.info(f"Parsed URL: {result}")

    if result and "error" not in result:
        user_id = get_user_id(result["url"])
        if user_id:
            if update_user(user_id, result["data"]):
                logger.info("Data updated successfully.")
            else:
                logger.error("Failed to update data.")
        else:
            logger.error("User ID not found.")
    else:
        logger.error("Parsing URL resulted in an error or empty result.")
