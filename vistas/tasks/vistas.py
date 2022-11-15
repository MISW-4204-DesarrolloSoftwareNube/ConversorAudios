
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
from modelos.modelos import Status, TaskSchema, Task, User_, User_Schema

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.cloud.storage import Blob
from google.cloud import storage

task_schema = TaskSchema()
user_schema = User_Schema()


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
        
        dir_name = '/home/RepositorioAudiosLocal/'
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        f = request.files['fileName']
        nameFile = name + '-' + str(task.id) + '.' + originalFormat
        f.save(os.path.join(dir_name, nameFile))

        client = storage.Client('ProyectoUniandesConversor')
        bucket = client.get_bucket('bucketproyectoaudiosv1')
        print("Mensaje: ", bucket)
        blob = Blob(nameFile, bucket)
        blob.upload_from_filename(dir_name + nameFile,'/')
        os.remove(dir_name + nameFile)
        #blob = Blob('pruebas5.txt', bucket)

        #blob.upload_from_filename('/home/gcastro0102/pruebabucket/pruebas5.txt','/')


        blob.make_public()

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
                client = storage.Client('ProyectoUniandesConversor')
                bucket = client.get_bucket('bucketproyectoaudiosv1')
                blob = bucket.blob(oldnewname)
                blob.delete()

                #origen = '/nfs/general/' + oldnewname
                #print(origen)
                #os.remove(origen)

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

        client = storage.Client('ProyectoUniandesConversor')
        bucket = client.get_bucket('bucketproyectoaudiosv1')
        if userTasks:
            userTask = Task.query.filter_by(id=id).first()

            if userTask:
                originalF = userTask.originalFormat
                sourceFormat = originalF.lower()
             
                newF = userTask.newFormat
                lastFormat = newF.lower()
                name = [value for value in userTask.fileName.split(".")][0]
                nameold = name + '-' + str(userTask.id) + '.' + sourceFormat
                namenew = name + '-' + str(userTask.id) + '.' + lastFormat
                if userTask.status == 2:
                    db.session.delete(userTask)
                    db.session.commit()
                    blobs = []
                    blobs.append(bucket.blob(nameold))
                    blobs.append(bucket.blob(namenew))
                    for blob in blobs:
                        blob.delete()
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
                    dictFiles["downloadFilesUploaded"].append("/nfs/general/"+userTask.fileName)
                if userTask.fileName == _filename and userTask.status == 2:
                    dictFiles["downloadFilesProcessed"].append("/nfs/general/"+userTask.fileName)
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
            
            client = storage.Client('ProyectoUniandesConversor')
            bucket = client.get_bucket('bucketproyectoaudiosv1')
            origen = name + '-' + str(task.id) + '.' + originalFormat
            print(origen)
            destino = name + '-' + str(task.id) + '.' + task.newFormat
            
            source_blob = bucket.blob(origen)
            #destination_bucket = client.Bucket

            blob_copy = bucket.copy_blob(source_blob, bucket, destino)
            
            task.status = Status.PROCESSED
            db.session.commit()

            user = User_.query.filter_by(id=task.usuario_id).first()

            self.enviar_email(user.email)
            """ if os.path.isfile(origen):
                print("Existe archivo -> " + origen)
                shutil.copy(origen, destino)

                task.status = Status.PROCESSED
                db.session.commit()

                
                user = User_.query.filter_by(id=task.usuario_id).first()
                
                
                self.enviar_email(user.email)
            else:
                print("Archivo no existe -> " + origen)"""
        return "archivos procesados correctamente"

    def enviar_email(self, receiver_email_):


        print("email a enviar: ", receiver_email_)
        sender_email = "conversor.grupo12@gmail.com"
        receiver_email = receiver_email_
        password = "dspleavntinppizy"

        message = MIMEMultipart("alternative")
        message["Subject"] = "multipart test"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = """\
        Archivo procesado"""
        html = """\
        <html>
              <body>
            <h1> Archivo procesado con exito!!!
            </h1>
          </body>
        </html>
        """
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")


        message.attach(part1)
        message.attach(part2)

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

        server.quit()
