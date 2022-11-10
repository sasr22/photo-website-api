FROM python:3.10.8-bullseye AS worker

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN apt-get update -y

RUN apt-get install firefox-esr -y

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz

RUN tar -xvzf geckodriver-v0.31.0-linux64.tar.gz

RUN rm geckodriver-v0.31.0-linux64.tar.gz

RUN chmod +x geckodriver

RUN mv geckodriver /usr/local/bin/

CMD [ "python", "main.py" ]