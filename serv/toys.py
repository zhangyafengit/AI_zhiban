from flask import Blueprint,request,send_file,jsonify
from bson import ObjectId
import setting
import os

toy = Blueprint("toy",__name__)

@toy.route("/bind_toy",methods=["POST"])
def bind_toy():
    toy_name = request.form.get("toy_name")
    baby_name = request.form.get("baby_name")
    remark = request.form.get("remark")
    user_id = request.form.get("user_id")
    device_key = request.form.get("device_key")

    #创建聊天窗口(chat_window)
    chat_window = setting.MONGO_DB.chat.insert_one({})

    # 获取当前用户的信息
    user_info = setting.MONGO_DB.users.find_one({"_id":ObjectId(user_id)})

    #创建玩具：
    res = _create_toy(toy_name=toy_name,baby_name=baby_name,remark=remark,device_key=device_key,user_id=user_id,chat_window=chat_window,nickname=user_info.get("nickname"))

    #给用户添加toys
    if not user_info.get("toys"):
        user_info["toys"] = []

    user_info["toys"].append(str(res.inserted_id))

    #将toys变为好友添加到用户的friend_list中
    if not user_info.get("friend_list"):
        user_info["friend_list"] = []

    friend_info={
        "friend_id":str(res.inserted_id),
        "toy_name":toy_name,
        "baby_name":baby_name,
        "avatar":"girl.jpg",
        "chat_id":str(chat_window.inserted_id)
    }

    user_info["friend_list"].append(friend_info)

    chat = setting.MONGO_DB.chat.find_one({"_id":chat_window.inserted_id})
    user_list = [str(res.inserted_id),user_id]
    chat["user_list"] = user_list
    chat["chat_list"] = []
    setting.MONGO_DB.chat.update({"_id":chat_window.inserted_id},{"$set":chat})


    setting.MONGO_DB.users.update_one({"_id":ObjectId(user_id)},{"$set":user_info})

    ret_str={
        "code":0,
        "msg":"玩具绑定成功"
    }
    return jsonify(ret_str)


@toy.route("/user_toy",methods=["POST"])
def user_toy():
    user_id = request.form.get("user_id")
    user_info = setting.MONGO_DB.users.find_one({"_id":ObjectId(user_id)})
    toy_list = user_info.get("toys")
    new_toy_list = []
    for i in toy_list:
        new_toy_list.append(ObjectId(i))

    toy_group = list(setting.MONGO_DB.toys.find({"_id":{"$in":new_toy_list}}))

    for index,toy in enumerate(toy_group):
        toy_group[index]["_id"] = str(toy["_id"])

    print(toy_group)

    return jsonify(toy_group)

@toy.route("/get_friend_list",methods=["POST"])
def get_friend_list():
    toy_id = request.form.get("toy_id")
    toy = setting.MONGO_DB.toys.find_one({"_id":ObjectId(toy_id)})
    toy["_id"] = str(toy["_id"])

    return jsonify(toy)

def _create_toy(**kwargs):
    #toy_name=toy_name,baby_name=baby_name,
    # remark=remark,device_key=device_key,
    # user_id=user_id,chat_window=chat_window ,nickname

    toy_info={
        "device_key":kwargs["device_key"],
        "toy_name":kwargs["toy_name"],
        "baby_name":kwargs["baby_name"],
        "bind_user":kwargs["user_id"],
        "avatar":"girl.jpg"
    }


    friend_list = [
        {
            "friend_id": kwargs["user_id"],
            "nickname":kwargs["nickname"],
            "remark": kwargs["remark"],
            "avatar": "girl.jpg",
            "chat_id": str(kwargs["chat_window"].inserted_id)
        }
    ]

    toy_info["friend_list"] = friend_list

    toy = setting.MONGO_DB.toys.insert_one(toy_info)

    return toy
