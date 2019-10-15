""" TODO: 待整理
"""
import re
from base64 import b64decode, b64encode
from calendar import monthrange
from datetime import datetime

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from django.conf import settings
from django.http import JsonResponse


def get_client_ip(request=None):
    if not request:
        from django_base.base_utils.middleware import get_request
        request = get_request()
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rsa_sign(text):
    key = RSA.importKey(b64decode(settings.ALIPAY_RSA_PRIVATE))
    h = SHA.new(text.encode())
    signer = PKCS1_v1_5.new(key)
    return b64encode(signer.sign(h)).decode()


def rsa_verify(text, sign):
    from base64 import b64decode
    public_key = RSA.importKey(b64decode(settings.ALIPAY_RSA_PUBLIC))
    sign = b64decode(sign)
    h = SHA.new(text.encode('GBK'))
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(h, sign)


def response_success(msg='', *, data=None, silent=False):
    payload = dict(ok=True)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    return JsonResponse(payload)


def response_fail(msg='', errcode=0, *, status=400, data=None, silent=False):
    payload = dict(ok=False)
    if msg:
        payload['msg'] = msg
    if silent:
        payload['silent'] = True
    if data:
        payload['data'] = data
    if errcode:
        payload['errcode'] = errcode
    return JsonResponse(payload, status=status)


# def sanitize_password(password):
#     """
#     :param password:
#     :return:
#     """
#     assert len(password) >= 6, '密码长度不得低于 6 位'
#     return password

def camel2underscore(name):
    # https://stackoverflow.com/a/1176023/2544762
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def normalize_date(dt):
    return datetime.strptime(dt, '%Y-%m-%d') if type(dt) == str else dt


def get_month_first_day(dt):
    dt = normalize_date(dt)
    return datetime(dt.year, dt.month, 1)


def get_month_last_day(dt):
    dt = normalize_date(dt)
    return datetime(dt.year, dt.month, monthrange(dt.year, dt.month)[1])


def get_year_first_day(dt):
    dt = normalize_date(dt)
    return datetime(dt.year, 1, 1)


def get_year_last_day(dt):
    dt = normalize_date(dt)
    return datetime(dt.year, 12, 31)


def get_quarter_first_day(dt):
    dt = normalize_date(dt)
    month = [0, 1, 1, 1, 4, 4, 4, 7, 7, 7, 10, 10, 10][dt.month]
    return datetime(dt.year, month, 1)


def get_quarter_last_day(dt):
    dt = normalize_date(dt)
    month = [0, 3, 3, 3, 6, 6, 6, 9, 9, 9, 12, 12, 12][dt.month]
    return datetime(dt.year, month, monthrange(dt.year, month)[1])


def earth_distance(lat1, lng1, lat2, lng2):
    """ 计算地球两点经纬度之间的距离 """
    # http://stackoverflow.com/a/19412565/2544762
    from math import sin, cos, sqrt, atan2, radians
    R = 6378.137 * 1000  # earth radius in meter
    lat1 = radians(lat1)
    lon1 = radians(lng1)
    lat2 = radians(lat2)
    lon2 = radians(lng2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def is_valid_mobile(mobile):
    """ 返回是否有效的手机号码格式 """
    # https://blog.csdn.net/voidmain_123/article/details/78962164
    # return bool(re.match(r'^(?:13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}$', mobile))
    return bool(re.match(r'^1[3-9]\d{9}$', mobile))


def get_district_names(district):
    import json
    import os.path
    area_data = json.load(open(
        os.path.join(os.path.dirname(__file__), 'data/china-area-data.json')))
    area_map = {}
    for sub in area_data.values():
        area_map.update(sub)
    result = []
    district = int(district)
    while district and area_map.get((str(district) + "000000")[:6]):
        result.insert(0, area_map.get((str(district) + "000000")[:6]))
        district //= 100
    return result


def wrap_choices(choices, value, default_value=None):
    for key, val in choices:
        if value == key:
            return val
    return default_value


def unwrap_choices(choices, value, default_value=None):
    for key, val in choices:
        if value == val:
            return key
    return default_value


def parse_excel_date(dt, format='%Y-%m-%d'):
    if not dt:
        return None
    elif type(dt) == int:
        return datetime.fromordinal(datetime(1900, 1, 1).toordinal() + dt - 2)
    return datetime.strptime(dt, format)

# class AESCipher:
#     class InvalidBlockSizeError(Exception):
#         """Raised for invalid block sizes"""
#         pass
#
#     def __init__(self, key):
#         self.key = key
#         self.iv = bytes(key[0:16], 'utf-8')
#         self.BS = 16
#         self.pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
#         self.unpad = lambda s: s[0:-ord(s[-1])]
#
#     def __pad(self, text):
#         from Crypto.Cipher import AES
#         text_length = len(text)
#         amount_to_pad = AES.block_size - (text_length % AES.block_size)
#         if amount_to_pad == 0:
#             amount_to_pad = AES.block_size
#         pad = chr(amount_to_pad)
#         return text + pad * amount_to_pad
#
#     def __unpad(self, text):
#         pad = ord(text[-1])
#         from Crypto.Cipher import AES
#         if text[-1] == '\0':
#             return text.rstrip('\0')
#         return text[:-pad] if pad <= AES.block_size else text
#
#     def encrypt(self, raw):
#         from Crypto.Cipher import AES
#         raw = self.__pad(raw)
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         return base64.b64encode(cipher.encrypt(raw))
#
#     def decrypt(self, enc):
#         from Crypto.Cipher import AES
#         enc = base64.b64decode(enc)
#         cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
#         data = cipher.decrypt(enc).decode().rstrip('\0')
#         return data
#         # return self.__unpad(cipher.decrypt(enc).decode())
