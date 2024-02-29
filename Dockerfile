FROM python:3.8-alpine
WORKDIR /unopad
RUN apk add gcc g++ make libffi-dev openssl-dev libxml2-dev libxslt-dev at
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./API ./API
WORKDIR /unopad/API
CMD atd ; uvicorn app:app --host 0.0.0.0 --port 4000
