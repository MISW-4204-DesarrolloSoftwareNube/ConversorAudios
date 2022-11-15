import requests, time
from celery_app import celery



@celery.task
def convertir_archivo():
    
    content = requests.post('http://34.111.232.31:80/api/files')
    
    return ("Respuesta: ",content.json())
