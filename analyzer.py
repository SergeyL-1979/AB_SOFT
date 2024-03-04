from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных
# DATABASE_URL = "mysql://username:password@localhost/dbname"
DATABASE_URL = "postgresql://postgres:wialon@localhost/avsoft"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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
