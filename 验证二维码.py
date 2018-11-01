import setting

def v_code(code):
    res = setting.MONGO_DB.devices.find_one({"device_key":code})
    return res


if v_code("1c9bddc0d0908e91039c08cf55e301da"):
    print("欢迎使用本公司产品")
else:
    print("请扫描玩具二维码")