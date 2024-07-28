from django.conf import settings
import hashlib


def md5(data_string):
    secret_Key = "django-insecure-j7%+%-&@ts99)x9bbo+d34uo(xej#z+&wg=c-o9ofn#zxm#gz*"

    obj = hashlib.md5(secret_Key.encode('utf-8'))
    obj.update(data_string.encode('utf-8'))
    return obj.hexdigest()
