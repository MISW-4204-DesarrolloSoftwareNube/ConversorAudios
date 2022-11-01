from beat_conf import beat_conf

broker_url = 'redis://localhost:6379/0'
result_backend='redis://localhost:6379/0'
task_serializar = 'json'
result_serializer = 'json'
enable_utc = True
imports = (
        "tasks"
)

# Diccionario con las tareas que queremos encolar
beat_schedule = beat_conf