FROM python:3.10.5-alpine3.16
WORKDIR /etl
COPY ./postgres_to_es/requirements.txt requirements.txt
RUN apk --no-cache add build-base && \
    apk --no-cache add linux-headers && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf requirements.txt
COPY ./postgres_to_es ./
RUN addgroup -g 2000 etl && \
    adduser -u 2000 -G etl -s /bin/sh -D etl
USER etl
ENTRYPOINT ["sh", "run.sh"]