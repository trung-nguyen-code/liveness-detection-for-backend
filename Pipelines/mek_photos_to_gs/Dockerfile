FROM python:3.9.6-slim-buster

ADD requirements.txt /
RUN pip install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD [ "python3" , "-u" , "mek_to_gs.py"]
