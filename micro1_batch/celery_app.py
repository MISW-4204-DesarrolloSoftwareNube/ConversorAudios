from celery import Celery 
import celeryconfig


celery = Celery('celery_app')

celery.config_from_object('celeryconfig')