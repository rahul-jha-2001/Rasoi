FROM python:latest

WORKDIR /app


COPY ./Cart .
COPY ./Cart/entrypoint.sh /usr/local/bin/entrypoint.sh

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:./proto"
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="${PYTHONPATH}:./proto"
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

EXPOSE 50051