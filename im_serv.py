from flask import Flask,request
from geventwebsocket.websocket import WebSocket
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from uuid import uuid4
from bson import ObjectId
from serv import chat
import json,os
import setting,baidu_ai,NLP



app = Flask(__name__)

user_socket_dict = {}

@app.route("/appwebsocket/<user_id>")
def appwebsocket(user_id):
    user_socket = request.environ.get("wsgi.websocket") # type:WebSocket
    if user_socket:
        user_socket_dict[user_id] = user_socket
        print(user_socket_dict)
    file_name = ""
    user_type = ""
    while True:
        user_msg = user_socket.receive()
        # {to_user:iwueroiuweior,send_music:abc.mp3}
        if type(user_msg) == bytearray:
            file_name = f"{uuid4()}.amr"
            file_path = os.path.join(setting.CHAT, file_name)
            with open(file_path, "wb") as f:
                f.write(user_msg)
            os.system(f"ffmpeg -i {file_path} {file_path}.mp3")
        else:
            user_msg_dict = json.loads(user_msg)
            user_type = user_msg_dict.get("type")

        if user_type and file_name:
            if user_type == "chat":
                to_user = user_msg_dict.get("to_user")
                touser_socket = user_socket_dict[to_user]
                msg_audio = _user_name(to_user, user_id)
                send_str = {
                    "form_user":user_id,
                    "content": msg_audio,
                    "type":"chat"
                }

                _redis_count(to_user,user_id)
                touser_socket.send(json.dumps(send_str))
                chat._chat_add_msg(user_id,to_user,f"{file_name}.mp3")
                user_type = ""
                file_name = ""

        # 与chat产生冲突
        # user_msg = user_socket.receive()
        # # {to_user:iwueroiuweior,send_music:abc.mp3}
        # user_msg_dict = json.loads(user_msg)
        # to_user = str(user_msg_dict.get("to_user"))
        # print(to_user)
        # touser = user_socket_dict.get(to_user) #type:WebSocket
        # print(touser)
        # ret_str = {
        #     "type":"music",
        #     "content":user_msg_dict.get("send_music")
        # }
        #
        # touser.send(json.dumps(ret_str))

@app.route("/toywebsocket/<user_id>")
def toywebsocket(user_id):
    user_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    if user_socket:
        user_socket_dict[user_id] = user_socket
        print(user_socket_dict)
    file_name = ""
    user_type = ""
    while True:
        user_msg = user_socket.receive()
        # {to_user:iwueroiuweior,send_music:abc.mp3}
        if type(user_msg) == bytearray:
            file_name = f"{uuid4()}.wav"
            file_path = os.path.join(setting.CHAT,file_name)
            with open(file_path,"wb") as f:
                f.write(user_msg)
        else:
            user_msg_dict = json.loads(user_msg)
            user_type = user_msg_dict.get("type")

        if user_type and file_name:
            if user_type == "music":
                ret_str = {
                    "type":"music",
                    "content":""
                }
                text = baidu_ai.audio2text(file_path)
                nlp_dict = NLP.my_nlp_lowB_plus(text,user_id)

                if nlp_dict.get("code"):
                    ret_str["type"] = "chat"
                    ret_str["form_user"] = nlp_dict.get("form_user")
                    mp3_name = baidu_ai.text2audio(nlp_dict.get("msg"))
                    ret_str["content"] = mp3_name
                else:
                    mp3_name = nlp_dict.get("msg")
                    ret_str["content"] = mp3_name

                user_socket.send(json.dumps(ret_str))

            if user_type == "chat":
                touser_socket = user_socket_dict.get(user_msg_dict.get("to_user"))
                ret_str = {
                    "type":user_type,
                    "content":file_name,
                    "form_user":user_id
                }

                _redis_count(user_msg_dict.get("to_user"),user_id)
                res = json.loads(setting.REDIS_DB.get(user_msg_dict.get("to_user")))
                count = sum(res.values())
                res["count"] = count
                print(res)
                touser_socket.send(json.dumps(res))
                chat._chat_add_msg(user_id, user_msg_dict.get("to_user"), file_name)

            user_type = ""
            file_name = ""

        # touser.send(user_msg_dict.get("send_music"))

def _user_name(to_user,user):
    toy = setting.MONGO_DB.toys.find_one({"_id":ObjectId(to_user)})
    print(toy.get("friend_list"))
    user_remark = [friend.get("remark") for friend in toy.get("friend_list") if friend.get("friend_id")==user][0]
    file_name = baidu_ai.text2audio(f"你有来自，{user_remark}，的消息")
    return file_name

def _redis_count(to_user,user_id):
    # to_user : 玩具  user_id：手机
    # redis 存储消息数量 def
    to_user_msg = setting.REDIS_DB.get(to_user)
    print(to_user_msg)

    if to_user_msg:
        count = json.loads(to_user_msg)
        if not count.get(user_id):
            count[user_id] = 1
        else:
            count[user_id] += 1
        redis_str = json.dumps(count)
    else:
        redis_str = json.dumps({user_id: 1})
        # setting.REDIS_DB.set(to_user, redis_str)

    setting.REDIS_DB.set(to_user, redis_str)

if __name__ == '__main__':
    http_serv = WSGIServer(("127.0.0.1",37210),app,handler_class=WebSocketHandler)
    http_serv.serve_forever()