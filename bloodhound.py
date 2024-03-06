from fastapi import FastAPI, HTTPException
import os
import shutil
import json
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.ERROR)  # Только ошибки будут записываться в файл
file_handler.setLevel(logging.INFO)  # Только ошибки будут записываться в файл
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
# logger.info("Сервер запущен и мониторит папку")

# Путь к папке для обработки файлов
folder_path = "soft/watched/folder"

# Путь к volume "Анализатора"
analyzer_volume = "soft/analyzer"

# Путь к volume "Ошибочников"
error_volume = "soft/errors"


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
        move_file(file_path, analyzer_volume)
        # Отправляем JSON-сообщение через очередь "Parsing"
        message = {"file_path": os.path.join(analyzer_volume, os.path.basename(file_path))}
        # Здесь должен быть код для отправки сообщения в очередь "Parsing"
    else:
        # Перемещаем не текстовый файл в volume "Ошибочников"
        move_file(file_path, error_volume)
        # Отправляем сообщение в "Errors"
        message = {"file_path": os.path.join(error_volume, os.path.basename(file_path))}
        # Здесь должен быть код для отправки сообщения в "Errors"


# Наследуемся от класса FileSystemEventHandler для обработки событий файловой системы
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:  # Игнорируем события о создании папок
            process_file(event.src_path)


# Создаем экземпляр наблюдателя
observer = Observer()
observer.schedule(MyHandler(), folder_path, recursive=False)
observer.start()


@app.on_event("shutdown")
def shutdown_event():
    observer.stop()
    observer.join()


@app.get("/")
async def index():
    logger.info("Сервер запущен и мониторит папку")
    return {"message": "Сервер запущен и мониторит папку"}

# ========================================================
# import os
# import json
# import logging
#
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
#
# from typing import List
# from fastapi import FastAPI, BackgroundTasks
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# FOLDER_TO_WATCH = "watched"
# ANALYZER_VOLUME = "analyzer"
# ERRORS_VOLUME = "errors"
# PARSING_QUEUE = "parsing"
#
#
# class FileEvent(BaseModel):
#     filename: str
#     event_type: str
#
#
# class FileHandler(FileSystemEventHandler):
#     def on_created(self, event):
#         if event.is_directory:
#             return
#         self.process_file(event.src_path)
#
#     def process_file(self, filepath):
#         try:
#             # Определение типа файла
#             if filepath.endswith('.txt'):
#                 destination = ANALYZER_VOLUME
#                 message = {"path": filepath}
#             else:
#                 destination = ERRORS_VOLUME
#                 message = {"error": "Unsupported file type", "path": filepath}
#
#             # Перемещение файла
#             new_filepath = os.path.join(destination, os.path.basename(filepath))
#             os.rename(filepath, new_filepath)
#
#             # Отправка сообщения в очередь
#             with open(PARSING_QUEUE, 'w') as queue_file:
#                 json.dump(message, queue_file)
#         except Exception:
#             logging.exception("Error moving file or sending message:")
#
#
# def start_watching():
#     event_handler = FileHandler()
#     observer = Observer()
#     observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
#     observer.start()
#     try:
#         while True:
#             pass
#     except KeyboardInterrupt:
#         observer.stop()
#     finally:
#         observer.join()
#
#
# app = FastAPI()
#
#
# @app.post("/start_watching/")
# async def start_watching_endpoint():
#     start_watching()
#     print(start_watching)
#     return {"message": "Watching started"}
