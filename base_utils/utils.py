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
    if not re.match(r'^\d{6}$', district):
        return district
    district = int(district)
    while district and area_map.get((str(district) + "000000")[:6]):
        result.insert(0, area_map.get((str(district) + "000000")[:6]))
        district //= 100
    # import gb2260
    # d = gb2260.get(district)
    # ' '.join([x.name for x in d.stack()])
    return result


def parse_choices(choices, delimiter='|'):
    if not choices:
        return ()
    if type(choices) == str:
        return parse_choices(choices=choices.split(delimiter))
    if type(choices[0]) == str:
        return tuple((c, c) for c in choices)
    return choices


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

def get_bank_data():
    return {"CDB": "国家开发银行", "ICBC": "中国工商银行", "ABC": "中国农业银行", "BOC": "中国银行", "CCB": "中国建设银行", "PSBC": "中国邮政储蓄银行",
            "COMM": "交通银行", "CMB": "招商银行", "SPDB": "上海浦东发展银行", "CIB": "兴业银行", "HXBANK": "华夏银行", "GDB": "广发银行",
            "CMBC": "中国民生银行", "CITIC": "中信银行", "CEB": "中国光大银行", "EGBANK": "恒丰银行", "CZBANK": "浙商银行",
            "BOHAIB": "渤海银行", "SPABANK": "平安银行", "SHRCB": "上海农村商业银行", "YXCCB": "玉溪市商业银行", "YDRCB": "尧都农商行",
            "BJBANK": "北京银行", "SHBANK": "上海银行", "JSBANK": "江苏银行", "HZCB": "杭州银行", "NJCB": "南京银行", "NBBANK": "宁波银行",
            "HSBANK": "徽商银行", "CSCB": "长沙银行", "CDCB": "成都银行", "CQBANK": "重庆银行", "DLB": "大连银行", "NCB": "南昌银行",
            "FJHXBC": "福建海峡银行", "HKB": "汉口银行", "WZCB": "温州银行", "QDCCB": "青岛银行", "TZCB": "台州银行", "JXBANK": "嘉兴银行",
            "CSRCB": "常熟农村商业银行", "NHB": "南海农村信用联社", "CZRCB": "常州农村信用联社", "H3CB": "内蒙古银行", "SXCB": "绍兴银行",
            "SDEB": "顺德农商银行", "WJRCB": "吴江农商银行", "ZBCB": "齐商银行", "GYCB": "贵阳市商业银行", "ZYCBANK": "遵义市商业银行",
            "HZCCB": "湖州市商业银行", "DAQINGB": "龙江银行", "JINCHB": "晋城银行JCBANK", "ZJTLCB": "浙江泰隆商业银行",
            "GDRCC": "广东省农村信用社联合社", "DRCBCL": "东莞农村商业银行", "MTBANK": "浙江民泰商业银行", "GCB": "广州银行", "LYCB": "辽阳市商业银行",
            "JSRCU": "江苏省农村信用联合社", "LANGFB": "廊坊银行", "CZCB": "浙江稠州商业银行", "DYCB": "德阳商业银行", "JZBANK": "晋中市商业银行",
            "BOSZ": "苏州银行", "GLBANK": "桂林银行", "URMQCCB": "乌鲁木齐市商业银行", "CDRCB": "成都农商银行", "ZRCBANK": "张家港农村商业银行",
            "BOD": "东莞银行", "LSBANK": "莱商银行", "BJRCB": "北京农村商业银行", "TRCB": "天津农商银行", "SRBANK": "上饶银行",
            "FDB": "富滇银行", "CRCBANK": "重庆农村商业银行", "ASCB": "鞍山银行", "NXBANK": "宁夏银行", "BHB": "河北银行",
            "HRXJB": "华融湘江银行", "ZGCCB": "自贡市商业银行", "YNRCC": "云南省农村信用社", "JLBANK": "吉林银行", "DYCCB": "东营市商业银行",
            "KLB": "昆仑银行", "ORBANK": "鄂尔多斯银行", "XTB": "邢台银行", "JSB": "晋商银行", "TCCB": "天津银行", "BOYK": "营口银行",
            "JLRCU": "吉林农信", "SDRCU": "山东农信", "XABANK": "西安银行", "HBRCU": "河北省农村信用社", "NXRCU": "宁夏黄河农村商业银行",
            "GZRCU": "贵州省农村信用社", "FXCB": "阜新银行", "HBHSBANK": "湖北银行黄石分行", "ZJNX": "浙江省农村信用社联合社", "XXBANK": "新乡银行",
            "HBYCBANK": "湖北银行宜昌分行", "LSCCB": "乐山市商业银行", "TCRCB": "江苏太仓农村商业银行", "BZMD": "驻马店银行", "GZB": "赣州银行",
            "WRCB": "无锡农村商业银行", "BGB": "广西北部湾银行", "GRCB": "广州农商银行", "JRCB": "江苏江阴农村商业银行", "BOP": "平顶山银行",
            "TACCB": "泰安市商业银行", "CGNB": "南充市商业银行", "CCQTGB": "重庆三峡银行", "XLBANK": "中山小榄村镇银行", "HDBANK": "邯郸银行",
            "KORLABANK": "库尔勒市商业银行", "BOJZ": "锦州银行", "QLBANK": "齐鲁银行", "BOQH": "青海银行", "YQCCB": "阳泉银行",
            "SJBANK": "盛京银行", "FSCB": "抚顺银行", "ZZBANK": "郑州银行", "SRCB": "深圳农村商业银行", "BANKWF": "潍坊银行",
            "JJBANK": "九江银行", "JXRCU": "江西省农村信用", "HNRCU": "河南省农村信用", "GSRCU": "甘肃省农村信用", "SCRCU": "四川省农村信用",
            "GXRCU": "广西省农村信用", "SXRCCU": "陕西信合", "WHRCB": "武汉农村商业银行", "YBCCB": "宜宾市商业银行", "KSRB": "昆山农村商业银行",
            "SZSBK": "石嘴山银行", "HSBK": "衡水银行", "XYBANK": "信阳银行", "NBYZ": "鄞州银行", "ZJKCCB": "张家口市商业银行",
            "XCYH": "许昌银行", "JNBANK": "济宁银行", "CBKF": "开封市商业银行", "WHCCB": "威海市商业银行", "HBC": "湖北银行", "BOCD": "承德银行",
            "BODD": "丹东银行", "JHBANK": "金华银行", "BOCY": "朝阳银行", "LSBC": "临商银行", "BSB": "包商银行", "LZYH": "兰州银行",
            "BOZK": "周口银行", "DZBANK": "德州银行", "SCCB": "三门峡银行", "AYCB": "安阳银行", "ARCU": "安徽省农村信用社",
            "HURCB": "湖北省农村信用社", "HNRCC": "湖南省农村信用社", "NYNB": "广东南粤银行", "LYBANK": "洛阳银行", "NHQS": "农信银清算中心",
            "CBBQS": "城市商业银行资金清算中心"}


def get_bank_info_by_account(account):
    import json
    from urllib.request import urlopen
    from urllib.parse import quote_plus
    resp = urlopen(r'https://ccdcapi.alipay.com/validateAndCacheCardInfo.json' +
                   r'?cardNo={}&cardBinCheck=true'.format(quote_plus(account)))
    result = json.loads(resp.read().decode())
    if not result['validated']:
        return False
    bank_data = get_bank_data()
    result['bankName'] = bank_data.get(result.get('bank'))
    return result
