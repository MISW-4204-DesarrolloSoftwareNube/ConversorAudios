from datetime import datetime
import os
import os.path
from time import sleep
from wsgiref import validate
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import requests
import time
import json
import shutil


import sys
sys.path.append('/home/ConversorAudios/modelos')
from modelos import db
from modelos import Status, TaskSchema, Task, User_, User_Schema

from google.cloud.storage import Blob
from google.cloud import storage

from google.cloud import pubsub_v1

import psycopg2


task_schema = TaskSchema()
user_schema = User_Schema()

from concurrent.futures import TimeoutError


credential_path = '/home/ConversorAudios/vistas/tasks/pub_sub_key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

timeout = 10

subscriber = pubsub_v1.SubscriberClient()
subscription_path = 'projects/proyectouniandescoversor/subscriptions/topic-conversor-sub'


def conversor_archivos(message):


    task_id= message.decode("utf-8")

    try:

        conn = psycopg2.connect(
            host="127.0.0.1",
            database="postgres",
            user="postgres",
            password="postgres",
            port=5432)
   
        cur = conn.cursor()
        cur.execute('SELECT * from task where id={}'.format(task_id))
        task = cur.fetchone()


        cur.close()

        statusUploaded = task[4]
        fileName = task[1]
        newFormat = task[3]

        if statusUploaded == 'UPLOADED':

            print('Procesar archivo ', task)
            originalFormat = [value for value in fileName.split(".")][-1]
            name = [value for value in fileName.split(".")][0]

            client = storage.Client('ProyectoUniandesConversor')
            bucket = client.get_bucket('bucketproyectoaudiosv1')
            origen = name + '-' + str(task_id) + '.' + originalFormat
            print("Source file: ",origen)
            destino = name + '-' + str(task_id) + '.' + newFormat

            print("Destination file: ",destino)

            source_blob = bucket.blob(origen)

            blob_copy = bucket.copy_blob(source_blob, bucket, destino)


            sql_update = """ UPDATE task
                SET status = %s
                WHERE id = %s"""

            cur = conn.cursor()
            cur.execute(sql_update,('PROCESSED',task_id))
            conn.commit()

            conn.close()
            print("Registro actualizado correctamente")

            # Falta ajustar envio de EMAIL en este Worker

            #self.enviar_email(user.email)

        else:
            print('No hago nada')

        #cur.close()

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)



def callback(message):
    #print(f'Received message 2: {message}')
    #print('Tarea a procesar: {}'.format(message.data))
    conversor_archivos(message.data)
    message.ack()


streaming_pull_future = subscriber.subscribe(subscription_path,callback=callback)
print(f'Listening form messages on {subscription_path}')



with subscriber:
    try:
        # streaming_pull_future.result(timeout=timeout)
        streaming_pull_future.result()


    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
