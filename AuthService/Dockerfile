FROM python:3.7-slim-buster

RUN pip3 install -U pip \
    && pip install setuptools \
    && pip install aiohttp pyjwt requests_async sqlalchemy \
    && rm -rf /root/.cache/pip/*

WORKDIR /opt/app/
CMD ["python3", "auth_service.py"]
