# ConversorAudios

# Pasos para la ejecución del proyecto OnPremise Conversor Audios
# Versión Python: Python 3.8.10 

 •	Clonar Repositorio Git: 

git clone https://github.com/MISW-4204-DesarrolloSoftwareNube/ConversorAudios.git 

•	Ingresar a la Rama: develop

git checkout develop

•	Ingresar al proyecto: 

cd ConversorAudios

•	Instalar entorno virtual Python:

python -m venv venv 

•	Habilitar el entorno virtual:

venv/scripts/actívate

Iniciar las instancias:

1.	Instancia Principal: Dentro del directorio principal 

ConversorAudios/flask run -p 5000 -h 0.0.0.0 

2.	Instancia micro1_batch: Ejecutar tarea del Celery

ConversorAudios/micro1_batch/celery -A tasks worker -l info 


3. Si desea ejecutar la tarea programada del Batch, se debe crear una tarea en Sistema operativo: Ver guia .pdf
