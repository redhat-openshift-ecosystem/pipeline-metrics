# fedora:44
FROM quay.io/fedora/fedora@sha256:b85ac08366be2c1576965a63afe2e58ababaed3024a64b723dae837d346185d4

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

COPY requirements.txt setup.py gunicorn.conf.py ./
COPY ./metrics ./metrics

RUN pip3 install --no-cache-dir -r requirements.txt && \
    python3 setup.py install -O1 --skip-build

RUN chgrp -R 0 /home/user /etc/passwd && \
    chmod -R g=u /home/user /etc/passwd

USER "${USER_UID}"

ENV HOME=/home/user

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "metrics.main:app" ]
