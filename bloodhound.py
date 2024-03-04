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

FOLDER_TO_WATCH = "watched"
ANALYZER_VOLUME = "analyzer"
ERRORS_VOLUME = "errors"
PARSING_QUEUE = "parsing"


class FileEvent(BaseModel):
    filename: str
    event_type: str


class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        self.process_file(event.src_path)

    def process_file(self, filepath):
        try:
            # Определение типа файла
            if filepath.endswith('.txt'):
                destination = ANALYZER_VOLUME
                message = {"path": filepath}
            else:
                destination = ERRORS_VOLUME
                message = {"error": "Unsupported file type", "path": filepath}

            # Перемещение файла
            new_filepath = os.path.join(destination, os.path.basename(filepath))
            os.rename(filepath, new_filepath)

            # Отправка сообщения в очередь
            with open(PARSING_QUEUE, 'w') as queue_file:
                json.dump(message, queue_file)
        except Exception:
            logging.exception("Error moving file or sending message:")


def start_watching():
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=FOLDER_TO_WATCH, recursive=False)
    observer.start()
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
