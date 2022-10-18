
from time import sleep
from wsgiref import validate
from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import requests
import time
import json

from modelos import db, Usuario, UsuarioSchema
   
usuario_schema = UsuarioSchema()


class VistaSignIn(Resource):

    def post(self):

        usuario = Usuario.query.filter(
            Usuario.usuario == request.json["usuario"]).first()
        if not usuario is None:
            return "No se puede crear el Apostador. El usuario ya existe", 409

        nuevo_usuario = Usuario(usuario=request.json["usuario"], contrasena=request.json["contrasena"])
        db.session.add(nuevo_usuario)
        db.session.commit()
        token_de_acceso = create_access_token(identity=nuevo_usuario.id)
        return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}

    def put(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = Usuario.query.get_or_404(id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        nombreUsuario = ""
        apostadorId = ""
        usuario = Usuario.query.filter(Usuario.usuario == request.json["usuario"],
                                       Usuario.contrasena == request.json["contrasena"]).first()
        db.session.commit()

        if usuario is None:
            return "El usuario no existe", 404
            
        token_de_acceso = create_access_token(identity=usuario.id)
        return {"mensaje": "Inicio de sesión exitoso", "token": token_de_acceso,
                "nombreUsuario": nombreUsuario, "apostadorId": apostadorId}


