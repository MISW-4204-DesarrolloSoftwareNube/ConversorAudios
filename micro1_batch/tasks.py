from flask_restful import Resource,Api
from flask import Flask, request 
import requests,json 
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')


# app = create_app('default')
# app_context = app.app_context()
# app_context.push()


# api = Api(app)

@app.task
def convertir_archivo():
    print("Hola-")
    content = requests.post('http://localhost:5000/api/files')

    print("valor: ",content.json())


# class VistaPuntaje(Resource):
#     def post(self,id_cancion):
#         # Recibir contendo en json
#         content = requests.get('http://127.0.0.1:5000/cancion/{}'.format(id_cancion))

#         if content.status_code == 404:
#             return content.json(),404
#         else:
#             cancion = content.json()
#             cancion['puntaje'] = request.json['puntaje']
#             args = (cancion,)
#             registrar_puntaje.apply_async(args)
#             return json.dumps(cancion)

# api.add_resource(VistaPuntaje,'/cancion/<int:id_cancion>/puntuar')