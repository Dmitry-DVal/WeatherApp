FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка Poetry и зависимостей
COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# Копируем проект
COPY . .

# Собираем статику
RUN python weathersite/manage.py collectstatic --noinput

# Gunicorn как сервер
CMD ["gunicorn", "--chdir", "weathersite", "--bind", "0.0.0.0:8000", "weathersite.wsgi:application"]
