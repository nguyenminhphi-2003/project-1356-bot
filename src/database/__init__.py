import database.models as models
import inspect
import logging

from peewee import SqliteDatabase

log = logging.getLogger(__name__)

def initialize_database(db_name):
    try:
        db = SqliteDatabase(db_name, pragmas={'foreign_keys': 1})
        models.db_proxy.initialize(db)
        db.connect()
        user_version = db.pragma("user_version")
        
        if user_version == 0:
            model_classes = [
                cls for name, cls in inspect.getmembers(models, inspect.isclass)
                if cls.__module__ == models.__name__ and hasattr(cls, '_meta')
            ]
            
            if model_classes:
                db.create_tables(model_classes)
                db.pragma("user_version", 1)
                log.info(f"Created {len(model_classes)} tables")
        
        log.info("Database connected successfully")
        
    except Exception as e:
        log.error(f"Database initialization failed: {e}")
        raise