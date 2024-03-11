import json
import os
import db_models
from datetime import datetime
from settings import *


# Get file info from DB
def get_file_from_db(db, file_id):
    return db.query(db_models.File).filter(db_models.File.file_id == file_id).first()


# Get file size

# Add file to DB
def add_file_to_db(db, **kwargs):
    new_file = db_models.File(
        file_id=kwargs['file_id'],
        file_name=kwargs['name'],
        file_description=kwargs['description'],
        file_type=kwargs['file_type'],
        file_size=kwargs['file_size'],
        file_creation_date=kwargs['file_creation_date'],
        file_modification_date=kwargs['file_modification_date'],
    )
    db.add(new_file)
    db.session.commit()
    db.refresh(new_file)
    return new_file


# Update file to DB
def update_file_in_db(db, **kwargs):
    updated_file = db.query(db_models.File).filter(db_models.File.file_id == kwargs['file_id']).first()
    updated_file.name = kwargs['name']
    updated_file.description = kwargs['description']
    updated_file.file_type = kwargs['file_type']  # .content_type
    updated_file.file_size = int(kwargs['file_size'])
    updated_file.file_creation_date = kwargs['file_creation_date']
    updated_file.file_modification_date = datetime.now()

    db.session.commit()
    db.refresh(updated_file)
    return updated_file


# Delete file from DB
def delete_file_from_db(db, file_info_from_db):
    db.delete(file_info_from_db)
    db.session.commit()
    return file_info_from_db
