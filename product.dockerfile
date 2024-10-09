FROM python:latest

WORKDIR /app


COPY ./Product .
COPY ./Product/entrypoint.sh /usr/local/bin/
COPY secrets.env .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

EXPOSE 50051


