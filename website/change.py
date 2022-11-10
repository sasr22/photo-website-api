import json
import os
from uuid import uuid4
from time import time
from datetime import datetime
from flask import Blueprint, request, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField
from wtforms.validators import DataRequired, Email, IPAddress
from defs import get_db, get_pika

class ForgotForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])
    ip = StringField("ip", validators=[DataRequired(), IPAddress()])

change_page = Blueprint("change", __name__)

@change_page.route("/change", methods=["GET", "POST"])
def change():
    if request.method == "GET":
        return render_template("change.html", remote_ip=request.remote_addr)

    form = ForgotForm()

    if form.validate():
        db = get_db()

        cursor = db.cursor()
        
        if cursor.execute("SELECT ip FROM api_tokens WHERE email=%s", (form.data.get("email"),)).fetchone() != None:
            channel = get_pika()

            channel.queue_declare(queue="email")

            uuid = str(uuid4())

            at = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")

            channel.basic_publish(exchange="", routing_key="email", body=json.dumps({
                "msg": f"Here is a link to confirm your request: {os.environ['URL']}confirm?uuid={uuid}&change=1, requested by: {request.remote_addr} at {at}, valid for 10 minutes",
                "type": "confirm",
                "email": form.data.get("email"),
            }))

            cursor.execute("INSERT INTO register_tokens VALUES(%s, %s, %s)", (uuid, form.data.get("email"), form.data.get("ip"),  ))

            db.commit()

            return render_template("change.html", remote_ip="", msgs=[f"Email sent!"]), 400
        return render_template("change.html", remote_ip="", msgs=["Email does not have a token"]), 400

    return {
        "email": form.email.errors,
        "ip": form.ip.errors,
    }, 400
