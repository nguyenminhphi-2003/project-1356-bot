from datetime import date
from peewee import *


db_proxy = DatabaseProxy()


class User(Model):
    username = CharField()
    telegram_id = CharField()
    created_at = TimestampField()
    
    class Meta:
        database = db_proxy
      
      
class Goal(Model):
    name = CharField()
    created_at = TimestampField()
    user = ForeignKeyField(User, backref='goals')
    
    class Meta:
        database = db_proxy
    
    
class Deadline(Model):
    deadline = DateField()
    country_timezone = CharField()
    user = ForeignKeyField(User, backref='deadline')
    
    class Meta:
        database = db_proxy