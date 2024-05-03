## Draft: flight search engine

Этот проект - прототип поисковика авиабилетов с пересадками, удобными для цифровых кочевников.
Когда удобно где-то лишний раз переночевать в отеле, поработать удаленно, посмотреть новый город
и потом со свежими силами и впечатлениями лететь дальше. 

[Подробнее про актуальность проекта](REASONING.md)

Проект состоит из бэкенда на Python и фронтенда на React.

Данные о рейсах берутся методом парсинга сайта aviasales.ru (далее - AS/АС) 

А конкретно - повторяя один из запросов, уходящих со страницы https://www.aviasales.ru/map

Полученные данные кешируются в директории lib/map_cache, чтобы не перегружать поисковик запросами.

Решаются две задачи:

1. Визуализация графа прямых рейсов между аэропортами.

2. Поиск "оптимального" маршрута между двумя аэропортами. (см. [TODO.md](TODO.md) для подробностей)

На текущей стаддии реализации отсутствует бОльшая часть необходимого пользовательского интерфейса и функционала АПИ на бекенеде.


![map demo](readme/map_demo.png)

![script demo](readme/script_demo.png)

Backend works on Python 3.10.12 for sure.

Use `pip install -r requirements.txt` to install all required packages.

`python app.py` to run the backend.

Frontend works on NodeJS 16.13.1 for sure.

`yarn` to install frontend dependencies.

`yarn start` to run the frontend.

Then go to http://localhost:3000 in your browser.

### See [TODO.md](TODO.md) for what to do.

Tests can be run with `pytest`