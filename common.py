from settings import REPLACEMENTS


def intify(string):
    try:
        return int(string)
    except:
        return string


def replace(message):
    for old, new in REPLACEMENTS.items():
        message.text = str(message.text).replace(old, new)
    return message

def diff(li1, li2):
    set_li1 = set(li1)
    set_li2 = set(li2)
    return list(list(set_li1 - set_li2) + list(set_li2 - set_li1))
