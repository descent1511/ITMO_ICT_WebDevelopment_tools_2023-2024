import requests
from bs4 import BeautifulSoup
import time
def parse_url(url: str) -> dict:
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
        
        total_stars = 0
        repo_list_items = soup.find_all('li', {'itemprop': 'owns'})
        for repo in repo_list_items:
            stars = repo.find('a', {'href': lambda x: x and x.endswith('/stargazers')})
            stars_count = int(stars.get_text(strip=True).replace(',', '')) if stars else 0
            total_stars += stars_count
        
        return {
            "url": tmp,
            "data": {
                "repositories": repo_count,
                "stars": total_stars
            }
        }

    except Exception as e:
        return {"error": str(e)}
