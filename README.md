# Бот сбора отзывов

Телеграм бот, для получения отзывов о Вкусно и точка в Уфе.

## Описание

Бот собирает отзывы за текущий день с сайта `https://ufa.flamp.ru/` и отправляет их на телефон пользователя.

## Функционал

Сбор данных раз в день на предмет новых отзывов.

Отправка отзывов на Телеграм пользователя в формате:

- Источник (в виде ссылки на отзыв);
- Автор;
- Дата / время;
- Рейтинг;
- Текст отзыва.

Хранение данных в БД SQLite.

## Установка

Клонировать репозиторий:

```python
git clone https://github.com/egorcoders/parser.git
```

Создать `.env` файл на уровне на уровне проекта с указаниме данных:

- TELEGRAM_TOKEN - Телеграм токен, специальный ключ от бота, с помощью которого его можно подключать к сторонним сервисам
- TELEGRAM_CHAT_ID - ID чата Телеграм
- ENDPOINT = 'https://ufa.flamp.ru/feed/'

Создать и активировать виртуальное пространство и установить зависимости:

Для Windows:

```python
cd parser
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Для Mac/Linux:

```python
cd parser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Для запуска бота, запустить файл parser_bot.py.
