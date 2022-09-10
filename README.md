[![Foodgram workflow](https://github.com/igor-isht/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master&event=push)](https://github.com/igor-isht/foodgram-project-react/actions/workflows/main.yml)

## Описание:

Foodgram - API к онлайн-сервису рецептов/продуктового помощника. На этом сервисе пользователи могут публиковать рецепты, 
подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
и перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Доступен по адресу [yourfoodgram.sytes.net](http://yourfoodgram.sytes.net/)

Документация на [yourfoodgram.sytes.net/api/docs/](http://yourfoodgram.sytes.net/api/docs/)


Используемый стек: Python, DjangoREST, PostgreSQL, Nginx, Docker


### Как запустить проект:

Необходимы командная оболочка bash и docker desktop.

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ln9var/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Создать файл с переменными окружения .env с настройками БД и со следующими ключами:


```
ENGINE=django.db.backends.postgresql     (+NAME, USER, PASSWORD, etc., в настройках заданы значения по умолчанию)

SECRET_KEY='Your_secret_key'

DEBUG=True  (по желанию)
```


Cоздать образ и контейнеры:

```

docker-compose up

docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py collectstatic --no-input

```
Готово. Проект развернулся на [localhost](http://localhost) 

Список эндпойнтов на http://localhost/api/docs/


## Авторы

[@igor-isht](https://github.com/igor-isht) - Бэкенд

[@yandex-praktikum](https://github.com/yandex-praktikum) - Фронтенд


