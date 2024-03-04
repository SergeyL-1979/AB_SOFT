import os
import json
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from typing import List
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем базовый класс для ORM
# Base = declarative_base()
# Подключение к базе данных
DATABASE_URL = "mysql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FOLDER_TO_WATCH = "soft/watched/folder/"
ANALYZER_VOLUME = "soft/analyzer/volume/"
ERRORS_VOLUME = "soft/errors/volume/"
PARSING_QUEUE = "soft/parsing/queue/"


class FileEvent(BaseModel):
    filename: str
    event_type: str


class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        logger.info(f"Detected new file: {event.src_path}")
        self.process_file(event.src_path)

    def process_file(self, filepath):
        try:
            # Определение типа файла
            if filepath.endswith('.txt'):
                destination = ANALYZER_VOLUME
                message = {"path": filepath}
                logger.info(f"{destination}: {message}")
            else:
                destination = ERRORS_VOLUME
                message = {"error": "Unsupported file type", "path": filepath}

            # Перемещение файла
            new_filepath = os.path.join(destination, os.path.basename(filepath))
            os.rename(filepath, new_filepath)
            logger.info(f"Moved file from {filepath} to {new_filepath}")

            # Отправка сообщения в очередь
            with open(PARSING_QUEUE, 'w') as queue_file:
                json.dump(message, queue_file)
            logger.info(f"Message sent to parsing queue for file: {filepath}")
        except Exception:
            logging.exception("Error moving file or sending message:")


def start_watching():
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
    observer.start()
    logger.info(f"Watching folder: {FOLDER_TO_WATCH}")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    finally:
        observer.join()


app = FastAPI()


@app.post("/start_watching/")
async def start_watching_endpoint():
    start_watching()
    print(start_watching)
    return {"message": "Watching started"}


# ==================================================================================================================



# Модель для хранения данных о словах и их количестве в базе данных
class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    count = Column(Integer)


# Создание таблицы в базе данных, если она еще не существует
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Модель для данных, которые мы получаем из очереди "Parsing"
class ParsingMessage(BaseModel):
    file_path: str
    text: str


# Метод для анализа текста и сохранения информации о словах в базе данных
def analyze_text(session, text: str):
    words = text.split()
    word_counts = {}
    for word in words:
        # Удаляем знаки препинания и приводим слово к нижнему регистру
        word = word.strip(".,!?").lower()
        if word:
            word_counts[word] = word_counts.get(word, 0) + 1

    for word, count in word_counts.items():
        # Проверяем, существует ли слово уже в базе данных
        db_word = session.query(Word).filter(Word.word == word).first()
        if db_word:
            db_word.count += count
        else:
            db_word = Word(word=word, count=count)
            session.add(db_word)

    session.commit()


# Метод обработки сообщений из очереди "Parsing"
def process_parsing_message(message: ParsingMessage):
    db = SessionLocal()
    analyze_text(db, message.text)
    db.close()


@app.post("/parse/")
async def parse(messages: List[ParsingMessage]):
    for message in messages:
        process_parsing_message(message)
    return {"message": "Parsing completed"}

# # Создаем модель для хранения данных в базе
# class WordCount(Base):
#     __tablename__ = 'word_counts'
#     id = Column(Integer, primary_key=True, index=True)
#     word = Column(String, index=True)
#     count = Column(Integer)
#
#
# # Инициализируем соединение с базой данных
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Создаем таблицы в базе данных
# Base.metadata.create_all(bind=engine)
#
#
# # Функция для обработки сообщений из очереди Parsing
# def process_parsing_message(message: dict, background_tasks: BackgroundTasks):
#     file_path = message.get('file_path')
#     if file_path.endswith('.txt'):
#         with open(file_path, 'r') as file:
#             text = file.read()
#             words = text.split()  # Разделяем текст на слова
#             for word in words:
#                 # Подсчитываем количество вхождений каждого слова
#                 word_count = len([w for w in words if w.lower() == word.lower()])
#                 # Сохраняем информацию в базе данных
#                 db = SessionLocal()
#                 db_word = WordCount(word=word.lower(), count=word_count)
#                 db.add(db_word)
#                 db.commit()
#                 db.close()
#
#
# # Маршрут для получения информации о текущем состоянии анализа
# @app.get("/analysis_state/")
# async def get_analysis_state():
#     db = SessionLocal()
#     word_counts = db.query(WordCount).all()
#     db.close()
#     return {"word_counts": [wc.word for wc in word_counts]}
#
#
# # Маршрут для обработки сообщений из очереди Parsing
# @app.post("/process_parsing_message/")
# async def process_parsing_message(background_tasks: BackgroundTasks, message: dict):
#     background_tasks.add_task(process_parsing_message, message, background_tasks)
#     return {"message": "Message processing started"}
