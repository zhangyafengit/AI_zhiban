from flask import Blueprint, request, send_file,jsonify
from bson import ObjectId
import setting
import os

cont = Blueprint("cont", __name__)


@cont.route("/content_list", methods=["POST"])
def content_list():
    res_list = list(setting.MONGO_DB.contents.find({}))
    for index,item in enumerate(res_list):
        res_list[index]["_id"] = str(item["_id"])

    return jsonify(res_list)

@cont.route("/content_one", methods=["POST"])
def content_one():
    content_id = request.form.get("content_id")
    res_one = setting.MONGO_DB.contents.find_one({"_id":ObjectId(content_id)})
    res_one["_id"] = str(res_one["_id"])

    return jsonify(res_one)