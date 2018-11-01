import requests
from uuid import uuid4
import hashlib,os
import setting

def CreateDevices(count):
    qr_list = []
    for i in range(count):
        md = hashlib.md5(str(uuid4()).encode("utf8"))
        qrcode = md.hexdigest()
        qr = requests.get(f"http://qr.liantu.com/api.php?text={qrcode}")
        qr_path = os.path.join(setting.QRCODE,f"{qrcode}.jpg")
        with open(qr_path , "wb") as f:
            f.write(qr.content)
        qrcode_dict = {
            "device_key" : qrcode
        }
        qr_list.append(qrcode_dict)

    res = setting.MONGO_DB.devices.insert_many(qr_list)

    return res


CreateDevices(5)