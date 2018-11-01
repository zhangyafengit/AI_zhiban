from flask import Blueprint,request,send_file
import setting
import os

gf = Blueprint("gf",__name__)

@gf.route("/get_content/<file_name>")
def get_content(file_name):
    file = os.path.join(setting.CONTENTS,file_name)
    return send_file(file)


@gf.route("/get_chat/<file_name>")
def get_chat(file_name):
    file = os.path.join(setting.CHAT,file_name)
    return send_file(file)