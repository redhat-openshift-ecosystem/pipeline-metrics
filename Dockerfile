FROM quay.io/fedora/fedora:41

LABEL description="Tekton metrics collector"
LABEL summary="A service that collects a metrics form Tekton pipelines."

ARG USER_UID=1000

USER root

RUN dnf update -y && \
    dnf install -y \
    gcc \
    git \
    krb5-devel \
    krb5-workstation \
    openssl-devel \
    pip \
    python3-devel && \
    dnf clean all

RUN useradd -ms /bin/bash -u "${USER_UID}" user
WORKDIR /home/user

COPY requirements.txt setup.py ./
COPY ./metrics ./metrics

RUN pip3 install --no-cache-dir -r requirements.txt && \
    python3 setup.py install -O1 --skip-build


USER "${USER_UID}"

ENTRYPOINT [ "metrics" ]
