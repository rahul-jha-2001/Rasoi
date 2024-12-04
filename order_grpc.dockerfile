FROM python:latest

WORKDIR /app


COPY ./Orders .
COPY ./Orders/grpc_entrypoint.sh /usr/local/bin/entrypoint.sh
COPY .env .

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:./proto"
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

EXPOSE 50051