from flask import Blueprint, request, send_file,jsonify
from bson import ObjectId
import setting
import os

u = Blueprint("u", __name__)


@u.route("/reg_user", methods=["POST"])
def reg_user():
    username = request.form["username"]
    password = request.form["password"]
    nickname = request.form["nickname"]
    gender = request.form["gender"]
    avatar = "boy.jpg" if gender=="1" else "girl.jpg"

    ret_str = {
        "code": 1,
        "msg":"注册失败"
    }

    insert_dict = {
        "username":username,
        "password":password,
        "nickname":nickname,
        "gender":gender,
        "avatar":avatar
    }

    res = setting.MONGO_DB.users.insert_one(insert_dict)
    res_id = str(res.inserted_id)
    if res_id :
        ret_str["code"] = 0
        ret_str["msg"] = "注册成功"
        ret_str["user_id"] = res_id


    return jsonify(ret_str)

@u.route("/user_info",methods=["POST"])
def user_info():
    user_id = request.form["user_id"]
    user_dict = setting.MONGO_DB.users.find_one({"_id":ObjectId(user_id)},{"password":0})

    user_dict["_id"] = str(user_dict["_id"])

    print(user_dict)

    return jsonify(user_dict)


@u.route("/user_login",methods=["POST"])
def user_login():
    username = request.form["username"]
    password = request.form["password"]
    print(username,password)
    user_dict = setting.MONGO_DB.users.find_one({"username":username,"password":password},{"password":0})
    if user_dict:
        user_dict["_id"] = str(user_dict["_id"])

    return jsonify(user_dict)