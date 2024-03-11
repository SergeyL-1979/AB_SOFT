from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# class Word(Base):
#     __tablename__ = "words"
#
#     id = Column(Integer, primary_key=True, index=True)
#     word = Column(String, index=True)
#     count = Column(Integer)

class File:
    __tablename__ = "files"

    file_id = Column(Integer)
    file_name = Column(String)
    file_description = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    file_creation_date = Column(DateTime)
    file_modification_date = Column(DateTime)

