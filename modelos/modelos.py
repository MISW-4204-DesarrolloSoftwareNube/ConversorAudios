from enum import Enum
import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    mail = db.Column(db.String(50))

class Status(Enum):
    UPLOADED = 1
    PROCESSED = 1

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    originalFormat = db.Column(db.String(3))
    newFormat = db.Column(db.String(3))
    status = Status
    date = db.Column(db.DateTime())

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True