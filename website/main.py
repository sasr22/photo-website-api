import os
from flask import Flask, g
from flask_wtf.csrf import CSRFProtect
from screenshot import screenshot_page
from delete import delete_page
from register import register_page
from confirm import confirm_page
from view import view_page
from change import change_page

app = Flask(__name__)

csrf = CSRFProtect(app)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

@app.teardown_appcontext
def close_pika(exception):
    channel = getattr(g, "_channel", None)
    if channel is not None:
        channel.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

app.register_blueprint(register_page)
app.register_blueprint(confirm_page)
app.register_blueprint(view_page)
app.register_blueprint(change_page)
app.register_blueprint(delete_page)
app.register_blueprint(screenshot_page)