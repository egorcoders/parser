import logging
import os
import re
import time
import datetime as dt
t = dt.datetime.now()

import requests
import telegram
from bs4 import BeautifulSoup as Bs
from dotenv import load_dotenv

load_dotenv()


class ServiceError(Exception):
    """Ошибка отсутствия доступа по заданному эндпойнту."""

    pass


class NetworkError(Exception):
    """Ошибка отсутствия сети."""

    pass


class EndpointError(Exception):
    """Ошибка, если эндпойнт не корректен."""

    pass


class MessageSendingError(Exception):
    """Ошибка отправки сообщения."""

    pass


class GlobalsError(Exception):
    """Ошибка, если есть пустые глобальные переменные."""

    pass


class DataTypeError(Exception):
    """Ошибка, если тип данных не dict."""

    pass


class ResponseFormatError(Exception):
    """Ошибка, если формат response не json."""

    pass


CONNECTION_ERROR = '{error}, {url}, {headers}, {params}'
SERVICE_REJECTION = '{code}'
WRONG_ENDPOINT = '{response_status}, {url}, {headers}, {params}'
WRONG_HOMEWORK_STATUS = '{homework_status}'
WRONG_DATA_TYPE = 'Неверный тип данных {type}, вместо "dict"'
STATUS_IS_CHANGED = '{verdict}, {homework}'
STATUS_IS_NOT_CHANGED = 'Статус не изменился, нет записей'
FAILURE_TO_SEND_MESSAGE = '{error}, {message}'
GLOBAL_VARIABLE_IS_MISSING = 'Отсутствует глобальная переменная'
GLOBAL_VARIABLE_IS_EMPTY = 'Пустая глобальная переменная'
MESSAGE_IS_SENT = 'Сообщение {message} отправлено'
FORMAT_NOT_JSON = 'Формат не json {error}'
LIST_IS_EMPTY = 'Список пустой'

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME_MINUTES = 330
ENDPOINT = os.getenv('ENDPOINT')

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def send_message(bot, message):
    """Отправляет сообщение пользователю в Телегу."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        raise MessageSendingError(FAILURE_TO_SEND_MESSAGE.format(
            error=error,
            message=message,
        ))
    logging.info(f'Message "{message}" is sent')


# def get_api_answer(current_timestamp):
#     """Делает запрос к единственному эндпоинту API-сервиса."""
#     timestamp = current_timestamp or int(time.time())
#     params = {'from_date': timestamp}
#     all_params = dict(url=ENDPOINT, headers=HEADERS, params=params)
#     try:
#         response = requests.get(**all_params)
#     except requests.exceptions.RequestException as error:
#         raise telegram.TelegramError(CONNECTION_ERROR.format(
#             error=error,
#             **all_params,
#         ))
#     response_status = response.status_code
#     if response_status != 200:
#         raise EndpointError(WRONG_ENDPOINT.format(
#             response_status=response_status,
#             **all_params,
#         ))
#     try:
#         return response.json()
#     except Exception as error:
#         raise ResponseFormatError(FORMAT_NOT_JSON.format(error))


# def check_response(response):
#     """
#     Возвращает домашку, если есть.
#     Проверяет валидность её статуса.
#     """
#     if 'code' in response:
#         raise ServiceError(SERVICE_REJECTION.format(
#             code=response.get('code'),
#         ))
#     if response['homeworks']:
#         return response['homeworks'][0]
#     else:
#         raise IndexError(LIST_IS_EMPTY)


# def parse_status(homework):
#     """Возвращает текст сообщения от ревьюера."""
#     if not isinstance(homework, dict):
#         raise DataTypeError(WRONG_DATA_TYPE.format(type(homework)))
#     homework_name = homework.get('homework_name')
#     homework_status = homework.get('status')

#     if homework_status not in HOMEWORK_STATUSES:
#         raise NameError(WRONG_HOMEWORK_STATUS.format(homework_status))

#     verdict = HOMEWORK_STATUSES[homework_status]

#     return f'Изменился статус проверки работы "{homework_name}". {verdict}'

def parse_status(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = t.strftime('%m/%d/%Y')
    html_text = requests.get(ENDPOINT)
    soup = Bs(html_text.text, 'lxml')
    reviews = soup.find_all(
        'li', class_='ugc-list__item js-ugc-list-item'
    )

    ans = ''
    personal_info = ''
    for review in reviews:
        review_date = review.select('cat-brand-ugc-date > a')[0].text.strip()
        company_name = review.select('cat-brand-name > a')[1].text.strip()
        if 'Сегодня' in review_date and company_name != 'Вектор':
            review_format_date = review_date.replace('Сегодня в', timestamp)
            review_url = (
                'Источник: ' + review.find(
                    'a', class_='link name t-text t-text--bold'
                ).get('href')
            )

            review_author = (
                'Автор: ' + review.select('cat-brand-name > a')[0].text.strip()
            )

            review_rating = 'Рейтинг: ' + review.find(
                'li', class_='review-estimation__item--checked'
            ).text.strip()

            review_text = ''
            comments = review.select('.t-text > .t-rich-text__p')
            for comment in comments:
                review_text += ' ' + comment.text.strip()

            review_text = 'Отзыв: ' + re.sub(
                r'^.*?Показать целиком ', '', review_text
            ).strip().replace('  ', ' ')

            personal_info = (
                review_url + '\n' +
                review_author + '\n' +
                review_format_date + '\n' +
                review_rating + '\n' +
                review_text + '\n'
            )

            ans += personal_info + '\n\n'

    return ans


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for key in (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ENDPOINT):
        if key is None:
            logging.error(GLOBAL_VARIABLE_IS_MISSING)
            return False
        if not key:
            logging.error(GLOBAL_VARIABLE_IS_EMPTY)
            return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise GlobalsError('Ошибка глобальной переменной. Смотрите логи.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            # response = get_api_answer(current_timestamp)
            # homework = check_response(response)
            message = parse_status(current_timestamp)
            send_message(bot, message)
            # logging.info(homework)
            # current_timestamp = response.get('current_date')
        except IndexError:
            message = 'Статус работы не изменился'
            send_message(bot, message)
            logging.info(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME_MINUTES)
        # logging.info(MESSAGE_IS_SENT.format(message))


if __name__ == '__main__':
    # logging.basicConfig(
    #     format='%(asctime)s, %(message)s, %(lineno)d, %(name)s',
    #     filemode='w',
    #     filename=f'{Path(__file__).stem}.log',
    #     level=logging.INFO,
    # )
    main()
