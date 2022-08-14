import time
import re
import datetime as dt

import requests
from bs4 import BeautifulSoup as Bs
t = dt.datetime.now()

def site_parsing():
    html_text = requests.get('https://ufa.flamp.ru/feed')
    current_date = t.strftime('%m/%d/%Y, %H:%M')
    soup = Bs(html_text.text, 'lxml')
    reviews = soup.find_all(
        'li', class_='ugc-list__item js-ugc-list-item'
    )

    for review in reviews:
        review_date = review.select('cat-brand-ugc-date > a')[0].text.strip()
        company_name = review.select('cat-brand-name > a')[0].text
        if 'Сегодня' in review_date:
            review_url = review.find('a', class_='link name t-text t-text--bold').get('href')
            review_author = review.select('cat-brand-name > a')[0].text.strip()
            review_rating = review.find(
                'li', class_='review-estimation__item--checked'
            ).text.strip()
            review_text = ''
            comments = review.select('.t-text > .t-rich-text__p')
            for comment in comments:
                review_text += ' ' + comment.text.strip()
            review_text = re.sub(r'^.*?Показать целиком ', '', review_text).strip().replace('  ', ' ')
            print(review_url, company_name, review_author, current_date, review_rating, review_text, sep='\n')
            print('')

        # company = review.select('.course-card-provider')[0].text
        # details = (
        #     review.find('div', class_='course-card-excerpt')
        #     .text.replace('…', '').replace('    ', ' ')
        #     .strip()
        # )
    #     if company == 'NextGen Learning':
    #         # with open(f'./logs/logs.txt', 'w') as f:
    #         print(
    #             f'Course name: {course_name} \n'
    #             f'Company: {company} \n'
    #             f'Details: {details}... \n'
    #         )


if __name__ == '__main__':
    while True:
        site_parsing()
        time_in_minutes = 3
        time.sleep(time_in_minutes)
