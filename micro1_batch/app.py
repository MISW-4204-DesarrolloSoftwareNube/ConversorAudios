
from tasks import convertir_archivo


CELERY_BEAT_SCHEDULE = {'add-every-30-seconds': {'task': 'tasks.convertir_archivo',
                                                 'schedule': 30.0,        'args': (),        'options': {'expires': 15.0, }, }, }
convertir_archivo()


