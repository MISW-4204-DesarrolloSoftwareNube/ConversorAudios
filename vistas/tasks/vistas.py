
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

from modelos import db
from modelos.modelos import Status, TaskSchema, Task

task_schema = TaskSchema()

class VistaTasks(Resource):

    def post(self):
        # File file = request.json["fileName"]
        print(request.form.get(""))
        originalFormat = [
            value for value in request.json["fileName"].split(".")][-1]
        task = Task(fileName=request.json["fileName"], originalFormat=originalFormat,
                    newFormat=request.json["newFormat"], status=Status.UPLOADED, date=datetime.now())
        db.session.add(task)
        db.session.commit()

        return "La tarea fue creada correctamente"

    @jwt_required()
    def get(self):
        return [task_schema.dump(ca) for ca in Task.query.all()]

class VistaTask(Resource):
    
    @jwt_required()
    def get(self, id):
        return task_schema.dump(Task.query.get_or_404(id))
