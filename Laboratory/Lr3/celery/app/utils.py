import requests
from bs4 import BeautifulSoup
import time
def parse_url(url: str):
    try:
        time.sleep(10)
        tmp = url
        if '?tab=repositories' not in url:
            url = url.rstrip('/') + '?tab=repositories'
        
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": f"Unable to access URL, status code: {response.status_code}"}

        soup = BeautifulSoup(response.content, 'html.parser')
        
        repo_count_elem = soup.find('span', {'class': 'Counter'})
        if repo_count_elem:
            repo_count = repo_count_elem.get_text(strip=True)
        else:
            repo_count = "No repositories found"
        print(repo_count)
        return {
            "url": tmp,
            "repositories": repo_count
        }

    except Exception as e:
        return {"error": str(e)}
