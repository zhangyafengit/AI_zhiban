from flask import Blueprint, request, send_file, jsonify
from bson import ObjectId
import setting
import pinyin
import os

fship = Blueprint("fship", __name__)


@fship.route("/add_req", methods=["POST"])
def add_req():
    device_key = request.form.get("friend_device_key")
    toy = setting.MONGO_DB.toys.find_one({"device_key": device_key})
    user_id = request.form.get("user_id")
    req_type = "user"
    if not user_id:
        user_id = request.form.get("toy_id")
        user = setting.MONGO_DB.toys.find_one({"_id": ObjectId(user_id)})
        req_type = "toy"
    else:
        user = setting.MONGO_DB.users.find_one({"_id": ObjectId(user_id)})

    name = user.get('nickname') if user.get('nickname') else user.get("baby_name")
    add_req_str = {
        "user_id": str(user.get("_id")),
        "avatar": user.get("avatar"),
        "name": name,
        "friend_id": str(toy.get("_id")),
        "content": f"{name}请求添加好友",
        "status": 0,
        "req_type": req_type
    }

    setting.MONGO_DB.friendship.insert_one(add_req_str)

    return jsonify({"code": 0, "msg": "请求发送成功"})


@fship.route("/req_list", methods=["POST"])
def req_list():
    user_id = request.form.get("user_id")
    user = setting.MONGO_DB.users.find_one({"_id": ObjectId(user_id)})
    toy_list = user.get("toys")

    request_list = list(setting.MONGO_DB.friendship.find({"friend_id": {"$in": toy_list}}))

    for index, req in enumerate(request_list):
        request_list[index]["_id"] = str(req.get("_id"))

    return jsonify(request_list)


@fship.route("/acc_req", methods=["POST"])
def acc_req():
    req_id = request.form.get("req_id")

    req = setting.MONGO_DB.friendship.find_one({"_id": ObjectId(req_id)})

    # 添加好友
    res = _add_friend(req.get("user_id"), req.get("friend_id"), req.get("req_type"), req.get("name"))

    setting.MONGO_DB.friendship.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})

    ret_str = {
        "code": 0,
        "msg": "添加好友成功"
    }
    return jsonify(ret_str)


def _add_friend(user_id, friend_id, add_type, remark):
    chat_window = setting.MONGO_DB.chat.insert_one({"user_list": [], "chat_list": []})
    if add_type == "toy":
        user_info = setting.MONGO_DB.toys.find_one({"_id": ObjectId(user_id)})
    else:
        user_info = setting.MONGO_DB.users.find_one({"_id": ObjectId(user_id)})

    friend_info = setting.MONGO_DB.toys.find_one({"_id": ObjectId(friend_id)})

    # user_info 是发起请求的用户或玩具
    # firend_info 是被添加好友的玩具，被添加好友的永远不可能是用户，只能是玩具

    # user_list 用来弥补 chat_window 的 user_list 空白
    user_list = [user_info.get("_id"), friend_info.get("_id")]

    # 互加好友:
    # 1.用户或玩具 添加 玩具 为好友
    user_add_friend = {
        "friend_id": str(friend_info.get("_id")),
        "toy_name": friend_info.get("toy_name"),
        "toy_name_pinyin": pinyin.to_pinyin(friend_info.get("toy_name")),
        "baby_name": friend_info.get("baby_name"),
        "baby_name_pinyin": pinyin.to_pinyin(friend_info.get("baby_name")),
        "avatar": friend_info.get("avatar"),
        "chat_id": str(chat_window.inserted_id)
    }
    if add_type != "toy":
        user_info["friend_list"].append(user_add_friend)
    else:
        user_add_friend = {
            "friend_id": str(friend_info.get("_id")),
            "nickname": friend_info.get("baby_name"),
            "nickname_pinyin": pinyin.to_pinyin(friend_info.get("baby_name")),
            "remark": remark,
            "remark_pinyin": pinyin.to_pinyin(remark),
            "avatar": friend_info.get("avatar"),
            "chat_id": str(chat_window.inserted_id)
        }
        user_info["friend_list"].append(user_add_friend)

    # 2.玩具 添加 用户或玩具 为好友
    nick = user_info.get("nickname") if user_info.get("nickname") else user_info.get("baby_name")
    friend_add_user = {
        "friend_id": str(user_info.get("_id")),
        "nickname": nick,
        "nickname_pinyin": pinyin.to_pinyin(nick),
        "remark": nick,
        "remark_pinyin": pinyin.to_pinyin(nick),
        "avatar": user_info.get("avatar"),
        "chat_id": str(chat_window.inserted_id)
    }

    friend_info["friend_list"].append(friend_add_user)

    # 更新一个 chat window
    setting.MONGO_DB.chat.update_one({"_id": chat_window.inserted_id}, {"$set": {"user_list": user_list}})
    # 更新:
    if add_type == "toy":
        setting.MONGO_DB.toys.update_one({"_id": ObjectId(user_id)}, {"$set": user_info})
    else:
        setting.MONGO_DB.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_info})

    setting.MONGO_DB.toys.update_one({"_id": ObjectId(friend_id)}, {"$set": friend_info})

    return True
