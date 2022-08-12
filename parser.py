import requests
from bs4 import BeautifulSoup as BS



page = 1

while True:
    r = requests.get('https://stopgame.ru/review/new/izumitelno/' + str(page))
    html = BS(r.content, 'html.parser')
    items = html.select('.items > .item')

    if len(items):
        count = 0
        for i in items:
            title = i.select('.article-description > .caption > a')
            print(title[0].text)
        page += 1
    else:
        break
