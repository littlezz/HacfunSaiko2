from peewee import *
from os.path import dirname
import os.path
from datetime import datetime
__author__ = 'zz'

# make sqlite file live in top level
db_dir = dirname(dirname(__file__))
db_name = 'db.sqlite3'


db = SqliteDatabase(os.path.join(db_dir, db_name))


class BaseModel(Model):
    class Meta:
        database = db

class Tasks(BaseModel):
    url = CharField(max_length=255)
    response_gt = IntegerField()
    create_time = DateTimeField(default=datetime.now())
    max_page = IntegerField()
    is_using = IntegerField(default=1)


def connect_to_db():
    db.connect()
    db.create_tables([Tasks], True)




def get_all():
    return Tasks.select().dicts()


def delete_by_id(id):
    q = Tasks.select().where(Tasks.id==id)
    if q.exists():
        obj = q.get()
        obj.delete_instance()



