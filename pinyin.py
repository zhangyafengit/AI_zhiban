from pypinyin import lazy_pinyin, TONE2

def to_pinyin(text):
    pinyin_list = lazy_pinyin(text,style=TONE2)
    py = "".join(pinyin_list)

    return py