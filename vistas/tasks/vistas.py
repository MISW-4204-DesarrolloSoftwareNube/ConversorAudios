
from datetime import datetime
import os
import os.path
import glob
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

        fileName = request.files['fileName'].filename
        originalFormat = [
            value for value in fileName.split(".")][-1]
        name = [
            value for value in fileName.split(".")][1]
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

        task = Task.query.get_or_404(id)

        if task.status == 2:
            oldname = task.fileName
            oldnewf = task.newFormat
            oldnewformat = oldnewf.lower()
            newfor = request.form.get("newFormat")
            newformat = newfor.lower()
            namefile = [value for value in oldname.split("/")][-1]
            nombresol = [value for value in namefile.split(".")][0]
            nombresolo = nombresol.lower()
            oldnewname = nombresolo+"."+oldnewformat
            newname = nombresolo+"."+newformat

            task.status = Status.UPLOADED
            db.session.commit()
            # obtener archivo
            songs = glob.glob("*."+oldnewformat)
            print(songs)

            for s in songs:

                song = s.lower()

                if (song == oldnewname):
                    # convertir archivo
                    print("song", s)
                    dst = newname

                    print(song, " y ", dst)

                    # absolute_path = os.path.dirname(__file__)
                    # print(absolute_path)

                    # p = open("audio.mp3")
                    # print("hola",p.re)

                    #sound = AudioSegment.from_file(absolute_path+"\\"+song, format=oldnewformat)
                    #sound = AudioSegment.from_mp3(absolute_path+"\\audio.mp3")
                    # print(sound)
                    #sound.export(dst, format=newformat)

                    task.newFormat = request.form.get("newFormat")
                    task.status = Status.PROCESSED
                    task.date = datetime.now()
                    db.session.commit()

                # eliminar archivo anterior convertido

                    return "El archivo fue modificado correctamente"

                else:

                    return "El archivo no fue encontrado", 400

        else:
            return "Este archivo no se ha procesado"

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
    @jwt_required()
    def post(self):
        tasks = Task.query.filter_by(status="UPLOADED").all()
        print(tasks)
        for task in tasks:
            originalFormat = [value for value in task.fileName.split(".")][-1]
            name = [value for value in task.fileName.split(".")][1]
            origen = 'C:\\audiofiles\\' + name + '-' + \
                str(task.id) + '.' + originalFormat
            print(origen)
            destino = 'C:\\audiofiles\\' + name + '-' + \
                str(task.id) + '.' + task.newFormat
            print(destino)
            shutil.copy(origen, destino)

            task.status = Status.PROCESSED
            db.session.commit()
