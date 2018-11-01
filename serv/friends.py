from flask import Blueprint, request, send_file,jsonify
from bson import ObjectId
import setting
import os

fri = Blueprint("fri", __name__)


@fri.route("/friend_list", methods=["POST"])
def friend_list():
    
    user_id = request.form.get("user_id")
    user_info = setting.MONGO_DB.users.find_one({"_id":ObjectId(user_id)})

    return jsonify(user_info.get("friend_list"))

