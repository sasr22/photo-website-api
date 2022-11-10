import json
import os
from uuid import uuid4
from flask import Blueprint, request
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, IntegerField, EmailField
from wtforms.validators import DataRequired, URL, AnyOf, UUID
from defs import get_db, get_pika

class ScreenshotForm(FlaskForm):
    uuid = EmailField("uuid", validators=[DataRequired(), UUID()])
    url = URLField("url", validators=[DataRequired(), URL()])
    format = StringField("format", validators=[DataRequired(), AnyOf(["webp", "jpg", "png"])])
    timeout = IntegerField("timeout", validators=[AnyOf([x for x in range(0, 21)])], default=5)

screenshot_page = Blueprint("screenshot", __name__)

@screenshot_page.route("/screenshot", methods=["GET"])
def screenshot():
    form = ScreenshotForm(request.args, meta={"csrf": False})

    if form.validate():
        db = get_db()

        cursor = db.cursor()

        data = cursor.execute("SELECT ip FROM api_tokens WHERE uuid=%s", (form.data.get("uuid"),)).fetchone()

        if data != None and data[0].replace(" ", "") == request.remote_addr:
            channel = get_pika()

            channel.queue_declare(queue="photo")

            uuid = str(uuid4())

            channel.basic_publish(exchange="", routing_key="photo", body=json.dumps({
                "url": form.data.get("url"),
                "format": form.data.get("format"),
                "uuid": uuid,
                "api_uuid": form.data.get("uuid"),
                "timeout": form.data.get("timeout")
            }))

            return {
                "photo_url": f"{os.environ['S3_URL']}/{form.data.get('uuid')}/{uuid}.{form.data.get('format')}"
            }

        return {
            "error": "IP and/or token does not match our records",
        }, 400

    return {
        "url": form.url.errors,
        "format": form.format.errors,
        "timeout": form.timeout.errors,
        "uuid": form.uuid.errors,
    }, 400