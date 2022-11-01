from beat_conf import beat_conf

broker_url = 'redis://192.168.1.8:6379/0'
result_backend='redis://192.168.1.8:6379/0'
task_serializar = 'json'
result_serializer = 'json'
enable_utc = True
imports = (
        "tasks"
)

# Diccionario con las tareas que queremos encolar
beat_schedule = beat_conf