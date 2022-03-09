FROM registry.fedoraproject.org/fedora:34

LABEL description="Tekton metrics collector"
LABEL summary="A service that collects a metrics form Tekton pipelines."

ARG USER_UID=1000

USER root

RUN dnf update -y && \
    dnf install -y \
    gcc \
    git \
    openssl-devel \
    pip \
    python3-devel && \
    dnf clean all

RUN useradd -ms /bin/bash -u "${USER_UID}" user
WORKDIR /home/user

COPY requirements.txt setup.py ./
COPY ./metrics ./metrics

RUN pip3 install -r requirements.txt
RUN python3 setup.py install -O1 --skip-build


USER "${USER_UID}"

ENTRYPOINT [ "metrics" ]
