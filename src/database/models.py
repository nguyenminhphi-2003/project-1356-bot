import datetime
from peewee import *


db_proxy = DatabaseProxy()


def default_datetime_field() -> DateTimeField:
    return DateTimeField(default=lambda: datetime.datetime.now())


class User(Model):
    username = CharField()
    telegram_id = CharField()
    chat_id = CharField()
    created_at = default_datetime_field()
    
    class Meta:
        database = db_proxy
      
      
class Goal(Model):
    name = CharField()
    created_at = default_datetime_field()
    user = ForeignKeyField(User, backref='goals')
    
    class Meta:
        database = db_proxy
    
    
class Deadline(Model):
    deadline = DateField()
    country_timezone = CharField()
    created_at = default_datetime_field()
    user = ForeignKeyField(User, backref='deadline')
    
    class Meta:
        database = db_proxy