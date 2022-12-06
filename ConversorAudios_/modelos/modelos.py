from datetime import datetime
from enum import Enum
import enum
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


db = SQLAlchemy()


class User_(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    task = db.relationship('Task', cascade='all, delete, delete-orphan')

class Status(enum.IntEnum):
    UPLOADED = 1
    PROCESSED = 2

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(100))
    originalFormat = db.Column(db.String(3))
    newFormat = db.Column(db.String(3))
    status = db.Column(db.Enum(Status))
    date = db.Column(db.DateTime(), default=datetime.now())
    usuario_id = db.Column(db.Integer, db.ForeignKey("user_.id"))


# class logBatch(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     procesDate = db.Column(db.DateTime(), default=datetime.now())
#     fileName = db.Column(db.String(50))
#     procesStatus = db.Column(db.String(50))
#     taskId = db.Column(db.Integer)
    

class User_Schema(SQLAlchemyAutoSchema):
    class Meta:
        model = User_
        load_instance = True

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True