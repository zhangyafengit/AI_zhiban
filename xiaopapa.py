import requests,json,os
import setting
from uuid import uuid4

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}



base_url_list = ["/ertong/424529/7713678",
                 "/ertong/424529/7713564",
                 "/ertong/424529/7713763",
                 "/ertong/424529/7713681",
                 "/ertong/424529/7713675"]
tag = "erge"
content_list = []


def xiaopachong(base_url,tag):

    content_id = base_url.rsplit("/",1)[-1]
    content_url = setting.XPP_URL + content_id +".json"
    name = uuid4()
    file_name_audio = f"{name}.mp3"
    file_name_jpg = f"{name}.jpg"
    file_name_audio_path = os.path.join(setting.CONTENTS,file_name_audio)
    file_name_jpg_path = os.path.join(setting.CONTENTS,file_name_jpg)

    res = requests.get(content_url, headers=header)
    res_dict = json.loads(res.content.decode("utf8"))
    print(res_dict)

    play_path = res_dict.get("play_path")

    cover_url = res_dict.get("cover_url")

    print(play_path,cover_url)

    play_content = requests.get(play_path)

    img = requests.get(cover_url)

    with open(file_name_audio_path,"wb") as f:
        f.write(play_content.content)

    with open(file_name_jpg_path,"wb") as f:
        f.write(img.content)


    content = {
        "title":res_dict.get("title"),
        "cover":file_name_jpg,
        "audio":file_name_audio,
        "detail":res_dict.get("intro"),
        "author":res_dict.get("nickname"),
        "tag":tag,
        "play_count":0
    }

    return content


for i in base_url_list:
    content_dict = xiaopachong(i,tag)
    content_list.append(content_dict)


contents_res = setting.MONGO_DB.contents.insert_many(content_list)

print(contents_res.inserted_ids)

