import requests
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def get_user_id(github_url: str) -> Any:
    try:
        api_get_user_id = "http://fastapi:8000/users/github"
        response = requests.get(api_get_user_id, params={"github": github_url})
        response.raise_for_status()
        user_data = response.json()
        return user_data.get("id")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get user ID: {e}")
        return None

def update_user(user_id: str, data : Dict[str, Any]) -> bool:
    try:
        api_update_repositories = f"http://fastapi:8000/users/{user_id}"
        response = requests.patch(api_update_repositories, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update data: {e}")
        return False
