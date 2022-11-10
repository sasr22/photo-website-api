import json
import os
from uuid import uuid4
from time import time
from datetime import datetime
from flask import Blueprint, request, render_template
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, Email, UUID
from defs import get_db, get_pika

class DeleteConfirmForm(FlaskForm):
    uuid = EmailField("uuid", validators=[DataRequired(), UUID()])

class DeleteForm(FlaskForm):
    email = EmailField("email", validators=[DataRequired(), Email()])

delete_page = Blueprint("delete", __name__)

@delete_page.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "GET":
        return render_template("delete.html", remote_ip=request.remote_addr)

    form = DeleteForm()

    if form.validate():
        db = get_db()

        cursor = db.cursor()
        
        if (data := cursor.execute("SELECT uuid FROM api_tokens WHERE email=%s", (form.data.get("email"),)).fetchone()) != None:
            channel = get_pika()

            channel.queue_declare(queue="email")

            uuid = str(uuid4())

            at = datetime.fromtimestamp(time()).strftime("%Y-%m-%d %H:%M:%S")

            channel.basic_publish(exchange="", routing_key="email", body=json.dumps({
                "msg": f"Here is a link to delete your token and email: {os.environ['URL']}delete/confirm?uuid={uuid}, requested by: {request.remote_addr} at {at}, valid for 10 minutes",
                "type": "delete",
                "email": form.data.get("email"),
            }))

            cursor.execute("INSERT INTO delete_tokens VALUES(%s, %s)", (uuid, data[0],  ))

            db.commit()

            return render_template("delete.html", remote_ip="", msgs=[f"Email sent!"]), 400
        return render_template("delete.html", remote_ip="", msgs=["Email does not have a token"]), 400

    return {
        "email": form.email.errors,
    }, 400

@delete_page.route("/delete/confirm", methods=["GET"])
def delete_confirm():
    form = DeleteConfirmForm(request.args, meta={"csrf": False})

    if form.validate():
        db = get_db()

        cursor = db.cursor()
        
        data = cursor.execute("SELECT api_uuid FROM delete_tokens WHERE uuid=%s", (form.data.get("uuid"),)).fetchone()

        if data != None:
            cursor.execute("DELETE FROM delete_tokens WHERE uuid=%s", (form.data.get("uuid"),))

            cursor.execute("DELETE FROM api_tokens WHERE uuid=%s", (data[0],))

            db.commit()

            return render_template("delete.html", remote_ip="", msgs=[f"Data deleted"]), 400
        return render_template("delete.html", remote_ip="", msgs=["Token expired or invalid"]), 400

    return {
        "uuid": form.uuid.errors,
    }, 400