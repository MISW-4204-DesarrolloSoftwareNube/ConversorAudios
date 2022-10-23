
from datetime import datetime
import os
import os.path
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

    #@jwt_required
    def post(self):
        fileName = request.files['fileName'].filename
        originalFormat = [
            value for value in fileName.split(".")][-1]
        name = [
            value for value in fileName.split(".")][1]
        task = Task(fileName=fileName, originalFormat=originalFormat,
                    newFormat=request.form.get("newFormat"), status=Status.UPLOADED, date=datetime.now())
        db.session.add(task)
        db.session.commit()

        dir_name = 'C:\\Users\\USER\\Documents\\'
        f = request.files['fileName']
        f.save(os.path.join(dir_name, name + '-' + str(task.id) + '.' + originalFormat))

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
        #obtener archivo

        oldname = "nombrearchivo.mp3"
        task = Task.query.get_or_404(id)
        
        if task.status == "PROCESSED":

            nombresolo = oldname.split(".")[0]
            format = request.json["newFormat"]
            newname = nombresolo+"."+format

            task.status=Status.UPLOADED
            db.session.commit()

            #convertir archivo
            # src = oldname
            # dst = newname
                                                          
            # sound = AudioSegment.from_mp3(src)
            # sound.export(dst, format="wav")

            task.fileName=newname
            task.newFormat=request.json["newFormat"]
            task.status=Status.PROCESSED 
            task.date=datetime.now()
            db.session.commit()

            #eliminar archivo anterior convertido
        
            return "El archivo fue modificado correctamente"

        else:
            return "Este archivo no se ha procesado"

class VistaFileProcessedByUser(Resource):
    @jwt_required()
    def get(self, id_user):
        
        userTasks = Task.query.filter_by(usuario_id=id_user).all()

        updatedFiles = []
        processedFiles = []


        dictFiles = {
            "listFilesUploaded": [],
            "listFilesProcessed":[]
        }

        if userTasks:

            for userTask in userTasks:
                if userTask.status == 1:
                    dictFiles["listFilesUploaded"].append(userTask.fileName)
                    # updatedFiles.append(userTask.fileName)
                    # print("Su archivo Original es : ",userTask.fileName)
                if userTask.status == 2:
                    dictFiles["listFilesProcessed"].append(userTask.fileName)

            print("El el usuario tiene los siguientes archivos : ", dictFiles)
           
            return json.dumps(dictFiles)

        else:
            return "El usuario no tiene documentos almacenados", 404
