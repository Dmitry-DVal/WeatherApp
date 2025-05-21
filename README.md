# Трекер погоды


### Описание
Веб-приложение для просмотра текущей погоды. Пользователь может зарегистрироваться и добавить в коллекцию одну или несколько локаций (городов, сёл, других пунктов), после чего главная страница приложения начинает отображать список локаций с их текущей погодой.

[Подробнее про ТЗ проекта](https://zhukovsd.github.io/python-backend-learning-course/projects/weather-viewer/)

[Дпелой приложения(доступен временно)](http://217.114.15.7)


### Мотивация проекта
- Реализация многопользовательского приложения
- Работа с внешними API


### Запуск приложения
1. Склонирyту репозиторий
2. Сконфигурируйте файл `.env` в соответствие с примером

```
.env
OW_API_KEY= действительный ключ OPENWEATHER_API_KEY, можно получить  https://openweathermap.org/

# Настройка Django
DJANGO_SECRET_KEY= django_secret_key # Секретный ключ Django
DEBUG=True/False
ALLOWED_HOSTS=217.114.15.7

# Настройка БД
DB_ENGINE=django.db.backends.postgresql
DB_NAME=weathersite_db
DB_USER=weathersite
DB_PASSWORD=your_password
DB_HOST=localhost 
DB_PORT=5432 # Порт PostgreSQL

```
3. Соберите и запустите контейнер. Выполните скрип из корневой директории проекта:

```bush
docker compose up -d --build
```

### Интерфейс приложения
![image alt](./images/screen_pk.jpg)

---
![image alt](./images/screen_sm.png)


### Функционал приложения
- Регистрация/Авторизация/Logout
- Поиск локаций по названию
- Добавление локация на главную страницу
- Удаление локаций


### Используемые технологии:
- Python
- Django/DjangoORM/Миграции
- Poetry
- Postgres
- HTML/CSS, Bootstrap
- unittest
- requests
- Docker/Docker Compose
- Nginx/Gunicorn


### Автор
[Дмитрий Валюженич](https://t.me/Dmitry_D321)
Mitya0777@gmail.com
