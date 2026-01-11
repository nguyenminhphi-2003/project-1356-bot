from datetime import date
from peewee import *


db_proxy = DatabaseProxy()


class User(Model):
    name = CharField()
    telegram_id = CharField()
    goal_end_date = DateField()
    
    class Meta:
        database = db_proxy
      
      
class Goal(Model):
    name = CharField()
    is_done = BooleanField()
    user = ForeignKeyField(User, backref='goals')
    
    class Meta:
        database = db_proxy
    