import os
from typing import List

import requests
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных
# DATABASE_URL = "mysql://username:password@localhost/dbname"
# DATABASE_URL = "mysql+pymysql://username:password@localhost/dbname"
DATABASE_URL = "postgresql://postgres:wialon@localhost/avsoft"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Создание таблицы в базе данных, если она еще не существует
Base.metadata.create_all(bind=engine)



