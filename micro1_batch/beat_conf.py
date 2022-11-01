from celery.schedules import crontab


beat_conf = {

    "task_1": {
        "task":"tasks.convertir_archivo",
        "schedule": crontab(minute="*/1"),
    },

    # "task_3": {
    #     "task":"tasks.scheduled_task_3",
    #     "schedule": crontab(minute="*/1"),
    #     "options":{
    #         # Se puede agregar rate limit, frecuencia de la tarea, tiempo que debe durar, y mas opciones mas
    #         "queue":"priority",
    #     },
    # },
    
}