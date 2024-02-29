import graypy
import logging
from starlette.background import BackgroundTask
from fastapi import Request, Response
from app import app
import os

log_file_name = os.getenv("log_file_name")
graylog_ip = os.getenv("graylog_ip")
graylog_port = os.getenv("graylog_port")

my_logger = logging.getLogger("Logger")
handler = graypy.GELFUDPHandler(graylog_ip, int(graylog_port))
logging.basicConfig(filename=log_file_name, level=logging.DEBUG)
my_logger.addHandler(handler)


def log_req_resp(request_url, request_method, response_body, response_statuscode):
    if response_statuscode == 200:
        my_logger.info(
            f"Request : {request_method} {request_url} - Response Status: {response_statuscode}"
        )
    else:
        my_logger.error(
            f"Request : {request_method} {request_url} - Response: {response_statuscode} {response_body.decode()}"
        )


@app.middleware("http")
async def log_middle(request: Request, call_next):
    request_url = request.url
    request_method = request.method
    response = await call_next(request)
    response_body = [chunk async for chunk in response.body_iterator]
    response_body = b"".join(response_body)
    task = BackgroundTask(
        log_req_resp, request_url, request_method, response_body, response.status_code
    )
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=task,
    )
