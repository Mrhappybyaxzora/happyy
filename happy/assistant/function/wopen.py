import requests
from bs4 import BeautifulSoup
from happy.logging import Logger
from functools import cache

l = Logger(__file__)


@cache
def wopen(app):
    sess = requests.Session()
    def extract_links(html):
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', {'jsname': 'UWckNb'})
        return [link.get('href') for link in links]

    def search_google(query):
        url = f"https://www.google.com/search?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
        response = sess.get(url, headers=headers)

        if response.status_code == 200:
            return response.text
        
        else:
            print("Failed to retrieve search results.")
            l.error(response.status_code)
        return None

    html = search_google(app)
    if html:
        links = extract_links(html)
        if links:
            return links[0]
        else:
            l.error(f"No links found for query: {app}")
            return f"https://www.google.com/search?q={app}"
    else:
        return f"https://www.google.com/search?q={app}"

if __name__ == "__main__":
    print(wopen("google"))