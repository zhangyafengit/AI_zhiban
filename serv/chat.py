from flask import Blueprint, request, send_file, jsonify
from bson import ObjectId
import setting
import os, json

imchat = Blueprint("imchat", __name__)


@imchat.route("/chat_list", methods=["POST"])
def chat_list():
    user_id = request.form.get('user_id')
    to_user = request.form.get('to_user')
    chat_window = setting.MONGO_DB.chat.find_one({"user_list": {"$all": [user_id, to_user]}})

    _ref_msg_count(user_id, to_user)

    return jsonify(chat_window.get("chat_list"))


@imchat.route("/recv_chat", methods=["POST"])
def recv_chat():
    user_id = request.form.get("user_id")
    sender = request.form.get("sender")

    user_msg_list = json.loads(setting.REDIS_DB.get(user_id))
    count = user_msg_list[sender]

    chat_window = setting.MONGO_DB.chat.find_one({"user_list": {"$all": [user_id, sender]}})
    chat_info = chat_window.get("chat_list")[-count:]
    for index, chat in enumerate(chat_info):
        chat_info[index]["type"] = "chat"
        chat_info[index]["form_user"] = sender

    _ref_msg_count(user_id, sender)
    return jsonify(chat_info)


@imchat.route("/chat_count", methods=["POST"])
def chat_count():
    user_id = request.form.get('user_id')
    count_dict = setting.REDIS_DB.get(user_id)
    if chat_count:
        count_dict = json.loads(count_dict)
        count_dict["count"] = sum(count_dict.values())
        return jsonify(count_dict)

    return jsonify({})


def _chat_add_msg(sender, to_user, msg):
    message = {
        "sender": sender,
        "content": msg
    }
    # chat_window = setting.MONGO_DB.chat.find_one({"user_lsit":{"$all":[sender,user]}})
    # chat_window["chat_list"].append(message)
    # "$push" : 在array最后插入一条内容  python：append
    setting.MONGO_DB.chat.update_one({"user_list": {"$all": [sender, to_user]}}, {"$push": {"chat_list": message}})


def _ref_msg_count(user_id, to_user):
    msg_dict = setting.REDIS_DB.get(user_id)
    print(msg_dict)
    if msg_dict:
        msg_dict = json.loads(msg_dict)
        msg_dict[to_user] = 0

    setting.REDIS_DB.set(user_id, json.dumps(msg_dict))
