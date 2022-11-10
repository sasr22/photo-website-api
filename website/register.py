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

class RegisterForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])
    ip = StringField("ip", validators=[DataRequired(), IPAddress()])

register_page = Blueprint("register", __name__)

@register_page.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", remote_ip=request.remote_addr)

    form = RegisterForm()

    if form.validate_on_submit():
        db = get_db()

        cursor = db.cursor()

        if (data := cursor.execute("SELECT created_at from register_tokens WHERE email=%s", (form.data.get("email"),)).fetchone()) == None:
            if cursor.execute("SELECT uuid from api_tokens WHERE email=%s", (form.data.get("email"),)).fetchone() == None:
                channel = get_pika()

                channel.queue_declare(queue="email")

                uuid = str(uuid4())

                channel.basic_publish(exchange="", routing_key="email", body=json.dumps({
                    "msg": f"Confirm your email by using this link: {os.environ['URL']}confirm?uuid={uuid}, Valid for 10 minutes",
                    "type": "register",
                    "email": form.data.get("email"),
                }))

                cursor.execute("INSERT INTO register_tokens VALUES(%s, %s, %s)", (uuid, form.data.get("email"), form.data.get("ip"), ))

                db.commit()

                return render_template("index.html", remote_ip="", msgs=["Email sent!"])
            return render_template("index.html", remote_ip="", msgs=["Email Taken!"]), 400
        
        if float(data[0]) + 60 < time():
            cursor.execute("DELETE FROM register_tokens WHERE email=%s", (form.data.get("email"),))
            
            channel = get_pika()

            channel.queue_declare(queue="email")

            uuid = str(uuid4())

            channel.basic_publish(exchange="", routing_key="email", body=json.dumps({
                "msg": f"Confirm your email by using this link: {os.environ['URL']}confirm?uuid={uuid}, Valid for 10 minutes",
                "type": "register",
                "email": form.data.get("email"),
            }))

            cursor.execute("INSERT INTO register_tokens VALUES(%s, %s, %s, %s)", (uuid, form.data.get("email"), form.data.get("ip"), ))

            db.commit()

            return render_template("index.html", remote_ip="", msgs=["Email sent!"])

        retry = datetime.fromtimestamp(float(data[0]) + 60, ).strftime("%Y-%m-%d %H:%M:%S")

        return render_template("index.html", remote_ip=request.remote_addr, msgs=[f"Please fill the form again after {retry} to resend the email!"]), 400

    return {
        "email": form.email.errors,
        "ip": form.ip.errors
    }, 400