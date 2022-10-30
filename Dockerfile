FROM ubuntu:20.04

WORKDIR /app

COPY requirements.txt requirements.txt
#RUN apt-get update && apt-get -y install python3-dev && python3 -m pip install --upgrade pip && pip install -r requirements.txt
RUN apt-get update && apt-get -y install python3-pip && pip install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]