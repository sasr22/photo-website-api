FROM python:3.10.8-alpine3.16 AS site

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY defs.py .

COPY init.py .

COPY main.py .

COPY change.py .

COPY confirm.py .

COPY delete.py .

COPY register.py .

COPY screenshot.py .

COPY view.py .

COPY templates ./templates

CMD [ "gunicorn", "-b", "0.0.0.0", "-w", "4", "main:app" ]