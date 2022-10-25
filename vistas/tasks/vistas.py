
from datetime import datetime
import os
import os.path
from time import sleep
from wsgiref import validate
from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt
import jwt
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import requests
import time
import json
import shutil

from modelos import db
from modelos.modelos import Status, TaskSchema, Task

task_schema = TaskSchema()


class VistaTasks(Resource):

    @jwt_required()
    def post(self):
        strJwtRequest = request.headers['Authorization']
        parseJtwData = strJwtRequest[7:]
        jwtDecoded = jwt.decode(parseJtwData, options={
                                "verify_signature": False})
        user_id = jwtDecoded['sub']

        fileN = request.files['fileName'].filename
        fileName = fileN.lower()
        originalFormat = [
            value for value in fileName.split(".")][-1]
        name = [
            value for value in fileName.split(".")][0]
        task = Task(fileName=fileName, originalFormat=originalFormat,
                    newFormat=request.form.get("newFormat"), status=Status.UPLOADED, date=datetime.now(), usuario_id=user_id)
        db.session.add(task)
        db.session.commit()

        dir_name = 'C:\\audiofiles\\'
        f = request.files['fileName']
        f.save(os.path.join(dir_name, name + '-' +
               str(task.id) + '.' + originalFormat))

        return "La tarea fue creada correctamente"

    @jwt_required()
    def get(self):
        return [task_schema.dump(ca) for ca in Task.query.all()]


class VistaTask(Resource):

    @jwt_required()
    def get(self, id):
        return task_schema.dump(Task.query.get_or_404(id))

    @jwt_required()
    def put(self, id):

        strJwtRequest = request.headers['Authorization']
        parseJtwData = strJwtRequest[7:]
        jwtDecoded = jwt.decode(parseJtwData, options={
                                "verify_signature": False})
        user_id = jwtDecoded['sub']

        task = Task.query.filter_by(usuario_id=user_id, id=id).first()

        if (task):

            if task.status == 2:
                taskname = task.fileName
                oldnewf = task.newFormat
                oldnewformat = oldnewf.lower()
                nombresol = [value for value in taskname.split(".")][0]
                nombresolo = nombresol.lower()
                oldnewname = nombresolo+'-'+str(id)+"."+oldnewformat

                task.status = Status.UPLOADED
                task.newFormat = request.form.get("newFormat")
                db.session.commit()

                origen = 'C:\\audiofiles\\' + oldnewname
                print(origen)
                os.remove(origen)

                return "La tarea ha sido actualizada correctamente"

            else:
                return "No se puede actualizar la tarea porque el archivo no se ha procesado"

        else:
            return "El id {} de la tarea, NO existe para el usuario {}".format(id, user_id)


    @jwt_required()
    def delete(self,id):

        strJwtRequest = request.headers['Authorization']
        parseJtwData = strJwtRequest[7:]

        jwtDecoded = jwt.decode(parseJtwData, options={
                                "verify_signature": False})
        user_id = jwtDecoded['sub']

        userTasks = Task.query.filter_by(usuario_id=user_id).all()

        if userTasks:
            userTask = Task.query.filter_by(id=id).first()
            if userTask:
                if userTask.status == 2:
                    db.session.delete(userTask)
                    db.session.commit()
                    return 'Tarea eliminada con exito', 202
                else:
                    return 'La tarea no tiene estado PROCESSED', 404
            else:
                return "El id {} de la tarea, NO existe para el usuario {}".format(id, user_id)
        else:
            return "El usuario NO tiene tareas creadas", 404


class VistaFileProcessedByUser(Resource):
    @jwt_required()
    def get(self, _filename):

        strJwtRequest = request.headers['Authorization']
        parseJtwData = strJwtRequest[7:]

        jwtDecoded = jwt.decode(parseJtwData, options={
                                "verify_signature": False})
        user_id = jwtDecoded['sub']

        userTasks = Task.query.filter_by(usuario_id=user_id).all()

        dictFiles = {
            "downloadFilesUploaded": [],
            "downloadFilesProcessed": []
        }

        if userTasks:
            for userTask in userTasks:
                if userTask.fileName == _filename and userTask.status==1:
                    dictFiles["downloadFilesUploaded"].append("C:/audiofiles/"+userTask.fileName)
                if userTask.fileName == _filename and userTask.status == 2:
                    dictFiles["downloadFilesProcessed"].append("C:/audiofiles/"+userTask.fileName)
            return json.dumps(dictFiles)
        else:
            return "El usuario NO! tiene tareas", 404



class VistaFiles(Resource):
    def post(self):
        tasks = Task.query.filter_by(status="UPLOADED").all()
        print(tasks)
        if not tasks:
            return "No hay archivos para procesar", 404
        for task in tasks:
            originalFormat = [value for value in task.fileName.split(".")][-1]
            name = [value for value in task.fileName.split(".")][0]
            origen = 'C:\\audiofiles\\' + name + '-' + \
                str(task.id) + '.' + originalFormat
            print(origen)
            destino = 'C:\\audiofiles\\' + name + '-' + \
                str(task.id) + '.' + task.newFormat
            if os.path.isfile(origen):
                print("Existe archivo -> " + origen)
                shutil.copy(origen, destino)

                task.status = Status.PROCESSED
                db.session.commit()
            else:
                print("Archivo no existe -> " + origen)
        return "archivos procesados correctamente"
