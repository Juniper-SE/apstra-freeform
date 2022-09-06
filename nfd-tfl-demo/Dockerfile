FROM ubuntu:20.04
USER root
RUN apt update
RUN apt install -y python3 python3-pip 
RUN python3 -V
RUN pip --version
RUN pip install virtualenv
RUN virtualenv /demo-venv
RUN . /demo-venv/bin/activate && pip install https://jenkins.dc1.apstra.com/view/OB/job/OB/job/AOS_latest_OB/lastSuccessfulBuild/artifact/bld/sdk_py3/dist/aos_sdk-0.1.0-py3-none-any.whl
