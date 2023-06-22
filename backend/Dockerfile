FROM docker.uclv.cu/python:3.9

WORKDIR /code/app

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade -r /code/requirements.txt

COPY ./app /code/app

# RUN cd app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
