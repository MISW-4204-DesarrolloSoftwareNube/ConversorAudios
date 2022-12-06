import os
from google.cloud import pubsub_v1

credential_path = '/home/ConversorAudios/vistas/tasks/pub_sub_key.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/proyectouniandescoversor/topics/topic-conversor'

data = 'Mensaje de prueba No. 00 - taskId: ###'

data = data.encode('utf-8')

future = publisher.publish(topic_path,data)
print(f'published message id {future.result()}')
