from flask import Blueprint,request,send_file,jsonify
import setting
import os

dev = Blueprint("dev",__name__)

@dev.route("/qrcode",methods=["POST"])
def qrcode():
    ret_str={
        "code":0,
        "msg":"感谢您的信任"
    }
    qr = request.form.get("qr")
    res = setting.MONGO_DB.devices.find_one({"device_key":qr})
    if not res:
        ret_str["code"] = 2
        ret_str["msg"] = "请扫描玩具二维码"
        return jsonify(ret_str)

    is_bind = setting.MONGO_DB.toys.find_one({"device_key":qr})
    if is_bind:
        ret_str["code"] = 1
        ret_str["msg"] = "添加好友"
        return jsonify(ret_str)

    return jsonify(ret_str)