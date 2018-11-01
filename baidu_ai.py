from uuid import uuid4
import setting
import os


def audio2text(file_path):
    cmd_str = f"ffmpeg -y -i {file_path} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {file_path}.pcm"
    os.system(cmd_str)
    file_content = ""
    with open(f"{file_path}.pcm", "rb") as f:
        file_content = f.read()

    res = setting.BAIDU_SPEECH.asr(file_content, "pcm", 16000, {
        "dev_pid": 1536
    })

    if res.get("result"):
        res_text = res.get("result")[0]
        print(res_text)
        return res_text
    else:
        print("语音识别失败")
        return "语音识别失败"

def text2audio(text):
    mp3_file = f"{uuid4()}.mp3"
    mp3_file_path = os.path.join(setting.CHAT, mp3_file)
    speech = setting.BAIDU_SPEECH.synthesis(text, "zh", 1, {
        "spd": 4,
        'vol': 8,
        "pit": 8,
        "per": 4
    })

    with open(mp3_file_path, "wb") as f:
        f.write(speech)

    return mp3_file

