from fastapi import FastAPI, HTTPException
import os
import shutil
import json
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from settings import ANALYZER_VOLUME, ERROR_VOLUME, FOLDER_PATH

app = FastAPI()

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Примеры обработчиков для вывода логов в консоль и файл
# Обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Обработчик для вывода логов в файл
file_handler = logging.FileHandler('app.log', encoding='utf-8')
file_handler.setLevel(logging.ERROR)  # Только ошибки будут записываться в файл
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger.info("Сервер запущен и мониторит папку")




# Функция для перемещения файла в указанный путь
def move_file(file_path, destination):
    try:
        shutil.move(file_path, destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка перемещения файла: {str(e)}")


# Функция для обработки файла
def process_file(file_path):

    # Проверяем тип файла
    if file_path.endswith(".txt"):  # Предположим, что txt - это текстовый формат
        # Перемещаем текстовый файл в volume "Анализатора"
        move_file(file_path, ANALYZER_VOLUME)

        # Отправляем JSON-сообщение через очередь "Parsing"
        message = {"file_path": os.path.join(ANALYZER_VOLUME, os.path.basename(file_path))}
        # Здесь должен быть код для отправки сообщения в очередь "Parsing"
        logger.info(message)
        print(message)
    else:
        # Перемещаем не текстовый файл в volume "Ошибочников"
        move_file(file_path, ERROR_VOLUME)
        # Отправляем сообщение в "Errors"
        message = {"file_path": os.path.join(ERROR_VOLUME, os.path.basename(file_path))}
        # Здесь должен быть код для отправки сообщения в "Errors"
        logger.info(message)


# Наследуемся от класса FileSystemEventHandler для обработки событий файловой системы
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:  # Игнорируем события о создании папок
            process_file(event.src_path)


# Создаем экземпляр наблюдателя
observer = Observer()
observer.schedule(MyHandler(), FOLDER_PATH, recursive=False)
observer.start()


@app.on_event("shutdown")
def shutdown_event():
    observer.stop()
    observer.join()


@app.get("/")
async def index():
    logger.info("Сервер запущен и мониторит папку")
    return {"message": "Сервер запущен и мониторит папку"}
