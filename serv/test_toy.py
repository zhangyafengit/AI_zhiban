from flask import Blueprint,request,send_file,render_template
import setting
import os

ttoy = Blueprint("ttoy",__name__)

@ttoy.route("/toy")
def toy():
    return render_template("speech.html")