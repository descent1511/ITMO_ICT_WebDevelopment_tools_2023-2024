# Celery + Redis

## `celery/main.py`
```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.tasks import parse_url_task

app = FastAPI()

class URLItem(BaseModel):
    url: str
 
@app.post("/parse-url/")
async def parse_url(item: URLItem, background_tasks: BackgroundTasks):
    background_tasks.add_task(parse_url_task, item.url)
    return {"message": "URL parsing has been started in the background."}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the URL parser API!"}

```
-   Строки 1-4: Импортируем необходимые модули из FastAPI и Pydantic, и импортируем функцию задачи из app.tasks.
-   Строка 6: Создаем экземпляр класса FastAPI.
-   Строки 9-11: Определяем модель Pydantic для проверки входящих данных URL.
-   Строки 13-17: Определяем POST конечную точку /parse-url/, которая принимает URL и запускает фоновую задачу для его анализа.
-   Строки 19-21: Определяем корневую GET конечную точку /, которая возвращает приветственное сообщение.

## `celery_app.py`
```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_app.conf.update(
    task_routes={
        "app.tasks.parse_url_task": "main-queue",
    },
)
```
-   Строка 1: Импортируем модуль Celery.
-   Строки 3-9: Инициализируем Celery приложение с именем worker и настраиваем его для использования Redis как брокера и backend.
-   Строки 11-15: Обновляем конфигурацию Celery для маршрутизации задачи parse_url_task в main-queue.

## `tasks.py`

```python
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
```

-   Строки 1-3: Импортируем Celery приложение, вспомогательную функцию для анализа URL и модуль requests.
-   Строки 5-8: Определяем задачу Celery parse_url_task, которая вызывает вспомогательную функцию parse_url и выводит результат.
-   Строки 10-13: Проверяем, является ли результат допустимым и не содержит ли ошибок.
-   Строки 14-32: Пытаемся получить ID пользователя из FastAPI сервиса и обрабатываем ответ.
-   Строки 33-40: Если ID пользователя найден, обновляем репозитории пользователя через FastAPI сервис и обрабатываем ответ.
-   Строки 42-43: Обрабатываем любые исключения, которые могут возникнуть во время HTTP запросов.