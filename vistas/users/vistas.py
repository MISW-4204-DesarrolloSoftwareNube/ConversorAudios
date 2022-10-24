
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

user_schema = UserSchema()

class VistaSignUp(Resource):

    def post(self):

        user = User.query.filter(
            User.username == request.json["username"]).first()
        if not user is None:
            return "No se puede crear el usuario, ya existe", 409
        if request.json["password1"] != request.json["password2"]:
            return "Las 2 contraseñas no coinciden", 409

        user = User.query.filter(
            User.email == request.json["email"]).first()
        if not user is None:
            return "No se puede crear el usuario, el email ya está registrado", 409

        new_user = User(
            username=request.json["username"], password=request.json["password"], email=request.json["email"])
        db.session.add(new_user)
        db.session.commit()
        token_de_acceso = create_access_token(identity=new_user.id)
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
