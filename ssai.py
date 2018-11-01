from flask import Flask
from serv import get_file
from serv import content
from serv import user
from serv import test_toy
from serv import toys
from serv import devices
from serv import friends
from serv import chat
from serv import friendship


app = Flask(__name__)
app.register_blueprint(get_file.gf)
app.register_blueprint(content.cont)
app.register_blueprint(user.u)
app.register_blueprint(test_toy.ttoy)
app.register_blueprint(toys.toy)
app.register_blueprint(devices.dev)
app.register_blueprint(friends.fri)
app.register_blueprint(chat.imchat)
app.register_blueprint(friendship.fship)


if __name__ == '__main__':
    app.run("127.0.0.1",9527,debug=True)