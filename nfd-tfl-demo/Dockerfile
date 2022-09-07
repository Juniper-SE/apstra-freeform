FROM ubuntu:20.04
USER root
COPY thirdparty/aos_sdk-0.1.0-py3-none-any.whl /aos_sdk-0.1.0-py3-none-any.whl
RUN apt update
RUN apt install -y python3 python3-pip
RUN python3 -V
RUN pip --version
RUN pip install virtualenv
RUN virtualenv /demo-venv
RUN . /demo-venv/bin/activate && pip install /aos_sdk-0.1.0-py3-none-any.whl
