FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем зависимости
WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root

# Копируем весь проект
COPY . .

# Собираем статику (если нужно)
RUN python weathersite/manage.py collectstatic --noinput

# Запускаем сервер
CMD ["python", "weathersite/manage.py", "runserver", "0.0.0.0:8000"]
