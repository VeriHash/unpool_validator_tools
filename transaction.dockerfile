FROM python:3.10-alpine

RUN apk update
RUN apk add git alpine-sdk make cmake

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "/transaction.py"]
