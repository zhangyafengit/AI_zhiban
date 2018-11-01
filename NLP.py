from bson import ObjectId
import requests, json
import jieba
import setting
import pinyin
from gensim import corpora
from gensim import models
from gensim import similarities

l1 = []
content = setting.MONGO_DB.contents.find()
for item in content:
    l1.append(item.get("title"))


def my_nlp_lowB(text, user_id=None):
    if "播放" in text:
        result_list = setting.MONGO_DB.contents.find()
        for i in result_list:
            if i.get("title") in text:
                return {"msg": i.get("audio"), "code": 0}

    if "发消息" in text or "聊天" in text or "说话" in text:
        user_info = setting.MONGO_DB.toys.find_one({"_id": ObjectId(user_id)})
        for friend in user_info.get("friend_list"):
            if friend.get("remark") in text or friend.get("nickname") in text:
                return {"code": 1, "msg": f"可以按消息键，给，{friend.get('remark')}，发消息了",
                        "form_user": friend.get("friend_id")}

    return {"msg": "我不知道你在说什么", "code": 1}


def my_nlp_lowB_plus(text, user_id=None):
    if "发消息" in text or "聊天" in text or "说话" in text:
        text_pinyin = pinyin.to_pinyin(text)
        user_info = setting.MONGO_DB.toys.find_one({"_id": ObjectId(user_id)})
        for friend in user_info.get("friend_list"):
            if friend.get("remark_pinyin") in text_pinyin or friend.get("nickname_pinyin") in text_pinyin:
                return {"code": 1, "msg": f"可以按消息键，给，{friend.get('remark')}，发消息了",
                        "form_user": friend.get("friend_id")}

    res = gensim_simnet(l1,text)
    if res:
        return {"msg": res.get("audio"), "code": 0}

    res = to_tuling(text,user_id)

    return {"msg": res, "code": 1}


def gensim_simnet(l1, a):
    all_doc_list = []
    for doc in l1:
        doc_list = [word for word in jieba.cut(doc)]
        all_doc_list.append(doc_list)
    doc_test_list = [word for word in jieba.cut(a)]
    dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
    corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    lsi = models.LsiModel(corpus)
    index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))
    sim = index[lsi[doc_test_vec]]
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    text = l1[cc[0][0]]
    print(a, text,cc[0][1])
    if cc[0][1] >= 0.75:
        res = setting.MONGO_DB.contents.find_one({"title": text})
        return res

def to_tuling(text,user_id):
    data = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": text
            }
        },
        "userInfo": {
            "apiKey": setting.API_KEY_TL,
            "userId": user_id
        }
    }

    res = requests.post(setting.TULING_URL, json.dumps(data))
    res = json.loads(res.content.decode("utf8"))
    res_text = res.get("results")[0].get("values").get("text")
    print(res_text)
    return res_text