FROM dockerhub.timeweb.cloud/library/python:3.9-slim

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY main.py .

# Объявляем, что тут будут важные данные
VOLUME /app/data

# Запускаем
CMD ["python", "main.py"]