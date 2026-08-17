# fedora:44
FROM quay.io/fedora/fedora:44

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

COPY pyproject.toml gunicorn.conf.py ./
COPY ./metrics ./metrics

RUN pip3 install -e .

RUN chgrp -R 0 /home/user /etc/passwd && \
    chmod -R g=u /home/user /etc/passwd

USER "${USER_UID}"

ENV HOME=/home/user

ENTRYPOINT [ "gunicorn", "-c", "gunicorn.conf.py", "metrics.main:app" ]
