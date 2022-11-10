import os
from flask import Blueprint, g
import pika
import psycopg

defs = Blueprint('defs', __name__)

def get_pika():
    channel = getattr(g, "_channel", None)
    if channel is None:
        credentials = pika.PlainCredentials(os.environ["PIKA_USER"], os.environ["PIKA_PASS"])
        connection = pika.BlockingConnection(pika.ConnectionParameters(os.environ["PIKA_URL"], int(os.environ["PIKA_PORT"]), "/", credentials))
        channel = g._channel = connection.channel()
    return channel

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = psycopg.connect(os.environ["DB_URI"])
    return db