import requests
import urllib.parse
import re

requestedResults = 0


def bingSearch(query):
    headers = {
        "Host": "www.bing.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"

    }
    r = requests.get("https://www.bing.com/search?q=" + urllib.parse.quote(f"{query}"), headers=headers, stream=True)
    print(r.content)
    return str(r.content)


def findQuizletMatches(webResponse):
    matches = re.findall(r"<li class=\"b_algo\"><h2><a href=\"(https:\/\/quizlet.*?)\"", webResponse)
    if len(matches) == 0:
        print("No Results!")
    else:
        if len(matches) <= 3:
            for i in matches:
                print(i)
        else:
            if requestedResults >= len(matches):
                for i in matches:
                    print(i)
            else:
                i = 0
                while i < requestedResults:
                    print(matches[i])
                    i = i + 1


searchQuery = input("Search Query: ")
requestedResults = int(input("Requested Results: "))
findQuizletMatches(bingSearch(searchQuery))
