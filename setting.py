import pymongo
import os
from aip import AipSpeech
from aip import AipNlp
import redis

#百度ai配置
APP_ID = '11562884'
API_KEY = '9iOLKP9VCo4nsEf3N8dcOUmT'
SECRET_KEY = 'aW0kwOHFbHrQely6bcmGTzU49t2jOYdL'
BAIDU_SPEECH = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
BAIDU_NLP = AipNlp(APP_ID, API_KEY, SECRET_KEY)

#图灵配置：
API_KEY_TL = "50530f837f3c4553af22b0ddb34e2543"

#数据库配置
conn = pymongo.MongoClient(host="127.0.0.1",port=27017)
MONGO_DB = conn["ssaidb"]
REDIS_DB = redis.Redis(host="127.0.0.1",port=6379,db=1)



#外链配置
XPP_URL = "http://m.ximalaya.com/tracks/"
TULING_URL = "http://openapi.tuling123.com/openapi/api/v2"


#目录配置
CONTENTS = os.path.join(os.path.dirname(__file__),"contents")
QRCODE = os.path.join(os.path.dirname(__file__),"qrcode")
CHAT = os.path.join(os.path.dirname(__file__),"chat")


# a = [1,2,3,4,5,6,7]
# print(a[-3:])