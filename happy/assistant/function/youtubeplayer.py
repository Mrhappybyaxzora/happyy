import requests
from happy.logging import Logger

l = Logger(__file__)

def playonyt(topic: str):
    url = f"https://www.youtube.com/results?q={topic}"
    count = 0
    cont = requests.get(url)
    data = cont.content
    data = str(data)
    lst = data.split('"')
    for i in lst:
        count += 1
        if i == "WEB_PAGE_TYPE_WATCH":
            break
    if lst[count - 5] == "/results":
        l.error("No results found for given query = " + topic)
        return "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xl"

    return f"https://www.youtube.com{lst[count - 5]}"