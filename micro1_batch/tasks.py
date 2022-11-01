import requests, time
from celery_app import celery



@celery.task
def convertir_archivo():
    
    content = requests.post('http://10.128.0.4:5000/api/files')
    
    return ("Respuesta: ",content.json())
