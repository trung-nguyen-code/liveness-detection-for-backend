FROM tensorflow/tensorflow:2.4.3-gpu

ENV PYTHONUNBUFFERED 1

WORKDIR /

COPY ./requirements.txt /requirements.txt
COPY ./mek_gs.json /mek_gs.json

RUN pip install -r /requirements.txt

RUN mkdir /trainer

COPY ./trainer /trainer/
ENTRYPOINT ["python", "-m", "trainer.task"]
