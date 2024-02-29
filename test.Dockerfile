FROM python:3.8-alpine
WORKDIR /unopad
RUN apk add gcc g++ make libffi-dev openssl-dev libxml2-dev libxslt-dev bash-completion
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./tests ./tests
COPY ./API ./tests/API
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait
CMD /wait && python -m pytest tests/run_tests.py