FROM python:3.10.8-alpine3.16 AS email-worker

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD [ "python", "main.py" ]