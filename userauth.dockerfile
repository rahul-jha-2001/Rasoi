FROM python:latest

WORKDIR /app


COPY ./UserAuth .
COPY  requirements.txt .
COPY ./UserAuth/entrypoint.sh /usr/local/bin/entrypoint.sh

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="${PYTHONPATH}:./proto"
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["entrypoint.sh"]

EXPOSE 50051