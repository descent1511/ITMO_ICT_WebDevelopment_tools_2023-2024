import multiprocessing
import requests
from bs4 import BeautifulSoup
from urls import urls
from db import add_page, Page

def parse_and_save(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.text.strip()
    try:
        page = Page(title=title)
        add_page(page)
    except Exception as e:
        print(f"Error while adding page: {e}")

def main():
    processes = []

    for url in urls:
        process = multiprocessing.Process(target=parse_and_save, args=(url,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("Execution time (process):", time.time() - start_time)
