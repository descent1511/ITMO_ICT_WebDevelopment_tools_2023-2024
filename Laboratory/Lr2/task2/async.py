import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urls import urls
from db import add_page, Page

async def fetch_page_title(session, url):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.title.text.strip()

async def parse_and_save(session, url):
    title = await fetch_page_title(session, url)
    try:
        page = Page(title=title)
        add_page(page)
    except Exception as e:
        print(f"Error while adding page: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import time
    start_time = time.time()
    asyncio.run(main())
    print("Execution time (async):", time.time() - start_time)
