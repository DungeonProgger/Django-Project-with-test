# Используем официальный Python 3.12 образ на базе slim
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Команда запуска приложения через gunicorn
CMD ["gunicorn", "cheese_shop.wsgi:application", "--bind", "0.0.0.0:8000"]
