from .celery_app import celery_app
from .utils import parse_url
import requests

@celery_app.task
def parse_url_task(url: str):
    result = parse_url(url)
    print(f"Parsed URL: {result}")

    if result and "error" not in result:
        try:

            api_get_user_id = "http://fastapi:8000/users/github"
            response_user_id = requests.get(api_get_user_id, params={"github": result["url"]})

            if response_user_id.status_code == 200:
                user_data = response_user_id.json()
                user_id = user_data.get("id")

                if not user_id:
                    print("User ID not found.")
                    return

                api_update_repositories = "http://fastapi:8000/users/{user_id}".format(user_id=user_id)
                data = {
                    "repositories": result["repositories"],
                }
                response_update = requests.patch(api_update_repositories, json=data)

                if response_update.status_code == 200:
                    print("Data updated successfully.")
                else:
                    print(f"Failed to update data. Status code: {response_update.status_code}, Response: {response_update.text}")

            else:
                print(f"Failed to get user ID. Status code: {response_user_id.status_code}, Response: {response_user_id.text}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while trying to update data: {e}")