ARG python_version=3.8

FROM python:${python_version}-alpine

ENV PIP_DISABLE_PIP_VERSION_CHECK=True
ENV PIP_NO_CACHE_DIR=true

WORKDIR /usr/local/src/encrypted-secrets

COPY setup.py .

# Install deps only.
RUN apk update \
 && apk upgrade \
 && apk add --no-cache --virtual .build-deps \
       gcc \
       make \
       gpgme-dev \
       musl-dev \
       linux-headers \
 && apk add --no-cache \
       gpgme \
 && pip3 install -e . \
 && pip3 uninstall -y encrypted-secrets \
 && apk del .build-deps

COPY . .

RUN pip3 install .

ENTRYPOINT ["encrypted-secrets"]
