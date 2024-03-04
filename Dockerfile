# Указывает Docker использовать официальный образ python 3 с dockerhub в качестве базового образа
FROM python:3.10.0-slim

# Устанавливает переменную окружения, которая гарантирует, что вывод из python будет отправлен прямо в терминал без предварительной буферизации
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

# Создаем каталог для нашего приложения внутри контейнера
RUN mkdir -p /usr/src/app

# Устанавливаем рабочий каталог контейнера — "/usr/src/app"
WORKDIR /usr/src/app

# Копируем файл requirements.txt в контейнер
COPY requirements.txt /usr/src/app/requirements.txt

# Устанавливаем зависимости, перечисленные в requirements.txt
RUN pip install -r requirements.txt

# Копируем все остальные файлы из текущего каталога в контейнер
COPY . /usr/src/app

# Это команда, которая будет запускать FastAPI приложение в контейнере
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
