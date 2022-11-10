from time import time
from flask import Blueprint, request, render_template
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.validators import DataRequired, UUID
from defs import get_db

class ViewForm(FlaskForm):
    uuid = EmailField("uuid", validators=[DataRequired(), UUID()])

view_page = Blueprint("view", __name__)

@view_page.route("/view", methods=["GET"])
def view():
    form = ViewForm(request.args, meta={"csrf": False})

    if form.validate():
        db = get_db()

        cursor = db.cursor()
        
        data = cursor.execute("SELECT created_at, api_uuid FROM view_tokens WHERE uuid=%s", (form.data.get("uuid"),)).fetchone()

        if data != None:
            if float(data[0]) + 60 * 10 >= time():
                cursor.execute("DELETE FROM view_tokens WHERE uuid=%s", (form.data.get("uuid"),))

                db.commit()

                return render_template("index.html", remote_ip="", msgs=[f"Token: {data[0]}, SAVE IT! The link is one time use!"]), 400
            return render_template("index.html", remote_ip="", msgs=["Token expired or invalid"]), 400
        return render_template("index.html", remote_ip="", msgs=["Token expired or invalid"]), 400

    return {
        "uuid": form.uuid.errors,
    }, 400