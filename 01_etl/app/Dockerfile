FROM python:3.10.5-alpine3.16
WORKDIR /app
COPY ../requirements.txt requirements.txt
RUN apk --no-cache add build-base && \
    apk --no-cache add linux-headers && \
    python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm -rf requirements.txt
COPY ./app ./
RUN addgroup -g 2000 app && \
    adduser -u 2000 -G app -s /bin/sh -D app
USER app
ENTRYPOINT ["sh", "run.sh"]