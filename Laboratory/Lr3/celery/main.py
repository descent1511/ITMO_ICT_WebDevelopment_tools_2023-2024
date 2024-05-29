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
