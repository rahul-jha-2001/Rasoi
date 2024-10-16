FROM python:latest

WORKDIR /app
COPY ./Restro_admin .
COPY ./Restro_admin/entrypoint.sh /usr/local/bin/
ENV PYTHONUNBUFFERED 1
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /usr/local/bin/entrypoint.sh
ENV PYTHONPATH="${PYTHONPATH}:./proto"


ENTRYPOINT ["entrypoint.sh"]

EXPOSE 8000
