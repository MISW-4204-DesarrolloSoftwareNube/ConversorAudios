
from datetime import datetime
from time import sleep
from wsgiref import validate
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import requests
import time
import json

from modelos import db, User, UserSchema
from modelos.modelos import Status, TaskSchema, Task

user_schema = UserSchema()
task_schema = TaskSchema()


class VistaSignUp(Resource):

    def post(self):

        user = User.query.filter(
            User.username == request.json["username"]).first()
        if not user is None:
            return "No se puede crear el Apostador. El usuario ya existe", 409

        new_user = User(
            username=request.json["username"], password=request.json["password"])
        db.session.add(new_user)
        db.session.commit()
        token_de_acceso = create_access_token(identity=user.id)
        return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": new_user.id}


class VistaLogIn(Resource):

    def post(self):
        user = User.query.filter(User.username == request.json["username"],
                                 User.password == request.json["password"]).first()
        db.session.commit()

        if user is None:
            return "El usuario no existe", 404

        token_de_acceso = create_access_token(identity=user.id)
        return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso,
                "User": user.username}


class VistaTasks(Resource):

    def post(self):
        # File file = request.json["fileName"]
        originalFormat = [
            value for value in request.json["fileName"].split(".")][-1]
        task = Task(fileName=request.json["fileName"], originalFormat=originalFormat,
                    newFormat=request.json["newFormat"], status=Status.UPLOADED, date=datetime.now())
        db.session.add(task)
        db.session.commit()

        return "La tarea fue creada correctamente"
