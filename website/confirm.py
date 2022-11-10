import json
import os
from uuid import uuid4
from time import time
from flask import Blueprint, request, render_template
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, UUID
from defs import get_db, get_pika

class ConfirmForm(FlaskForm):
    uuid = EmailField("uuid", validators=[DataRequired(), UUID()])

confirm_page = Blueprint("confirm", __name__)

@confirm_page.route("/confirm", methods=["GET"])
def confirm():
    form = ConfirmForm(request.args, meta={"csrf": False})

    if form.validate():
        db = get_db()

        cursor = db.cursor()

        data = cursor.execute("SELECT created_at, email, ip FROM register_tokens WHERE uuid=%s", (form.data.get("uuid"),)).fetchone()

        if data != None:
            if float(data[0]) + 60 * 10 >= time():
                if request.args.get("change", 0, type=int) == 1:
                    cursor.execute("DELETE FROM api_tokens WHERE email=%s", (data[1],))

                channel = get_pika()

                channel.queue_declare(queue="email")

                token = str(uuid4())
                
                uuid = str(uuid4())

                channel.basic_publish(exchange="", routing_key="email", body=json.dumps({
                    "msg": f"Here is a link to view your token: {os.environ['URL']}view?uuid={uuid}, valid for 10 minutes",
                    "type": "confirm",
                    "uuid": token,
                    "email": data[1],
                }))

                cursor.execute("INSERT INTO api_tokens VALUES(%s, %s, %s)", (token, data[1], data[2],  ))

                cursor.execute("INSERT INTO view_tokens VALUES(%s, %s)", (uuid, token,  ))

                cursor.execute("DELETE FROM register_tokens WHERE uuid=%s", (form.data.get("uuid"), ))

                db.commit()
        
                return render_template("index.html", remote_ip="", msgs=["Email with link sent!"])
            return render_template("index.html", remote_ip="", msgs=["Token expired or invalid"]), 400
        return render_template("index.html", remote_ip="", msgs=["Token expired or invalid"]), 400

    return {
        "token": form.uuid.errors,
    }, 400