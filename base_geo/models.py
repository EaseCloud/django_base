import json

from django.conf import settings
from django.db import models


class GeoPositionedModel(models.Model):
    """ 包含地理位置的模型
    """

    # 地球半径（米）
    EARTH_RADIUS = 6378245.0

    geo_lng = models.FloatField(
        verbose_name='经度',
        default=0,
        blank=True,
    )

    geo_lat = models.FloatField(
        verbose_name='纬度',
        default=0,
        blank=True,
    )

    radius = models.FloatField(
        verbose_name='半径',
        default=0,
        blank=True,
    )

    geo_label = models.CharField(
        verbose_name='位置标签',
        max_length=255,
        blank=True,
        default='',
    )

    adcode = models.IntegerField(
        verbose_name='行政区划编码',
        default=0,
        help_text='保存时试图自动获取区划编码',
    )

    geo_info = models.TextField(
        verbose_name='地理信息',
        default='',
        blank=True,
        help_text='保存时自动尝试获取地理信息',
    )

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     print('save geo positioned model')
    #     # TODO: 此类可能引起挂起的操作需要考虑放到 Celery 队列处理
    #     # 自动解析地理位置（百度借口）
    #     if settings.AUTO_GEO_DECODE:
    #         try:
    #             info = self.get_geo_decode()
    #             self.geo_info = json.dumps(info)
    #             self.adcode = info.get('addressComponent').get('adcode')
    #         except:
    #             pass
    #     super(GeoPositionedModel, self).save(self, *args, **kwargs)

    def parse_location(self):
        """ 根据坐标解析地址 """
        try:
            info = self.get_geo_decode()
            self.geo_info = json.dumps(info)
            self.adcode = info.get('addressComponent').get('adcode')
            self.geo_label = info.get('formatted_address')
        except:
            pass
        self.save()

    @staticmethod
    def inside_china(lat, lng):
        """ 粗算坐标是否在国内
        :param lat:
        :param lng:
        :return:
        """
        return 73.66 < lng < 135.05 and 3.86 < lat < 53.55

    @staticmethod
    def latlng_baidu2qq(lat, lng):
        """ 百度地图坐标转换成QQ地图坐标
        :param lat:
        :param lng:
        :return:
        """
        import math
        x_pi = math.pi * 3000.0 / 180.0
        x = lng - 0.0065
        y = lat - 0.006
        z = (x * x + y * y) ** 0.5 - 0.00002 * math.sin(y * x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
        lng = z * math.cos(theta)
        lat = z * math.sin(theta)
        return lat, lng

    def geo_qq(self):
        """ 获取 qq 坐标系的坐标（纬度latitude，经度longitude）
        :return:
        """
        return self.latlng_baidu2qq(self.geo_lat, self.geo_lng)

    @staticmethod
    def geo_decode(lat, lng, platform='BMAP'):
        """ 调用百度接口反解地理信息
        :param lat: 经度
        :param lng: 纬度
        :param platform: BAIDU/GAODE 百度/高德
        :return:
        """
        from urllib.request import urlopen
        try:
            if platform == 'BMAP':
                resp = urlopen(
                    'http://api.map.baidu.com/geocoder/v2/'
                    '?location={},{}&output=json&ak={}'.format(lat, lng, settings.BMAP_KEY)
                )
                return json.loads(resp.read().decode()).get('result')
            elif platform == 'AMAP':
                resp = urlopen(
                    'https://restapi.amap.com/v3/geocode/regeo'
                    '?key={key}&location={lng},{lat}'.format(lat=lat, lng=lng, key=settings.AMAP_KEY)
                )
                data = json.loads(resp.read().decode())
                return data.get('regeocode')
        except:
            # 反解地理信息失败
            import traceback
            from sys import stderr
            print(traceback.format_exc(), file=stderr)
            return None

    def get_geo_decode(self, platform='BMAP'):
        return self.geo_decode(self.geo_lat, self.geo_lng, platform)

    def get_label(self):
        info = self.get_geo_decode()
        return info and info.get('formatted_address')

    def get_district_number(self):
        info = self.get_geo_decode()
        address = info and info.get('addressComponent')
        return address and address.get('adcode')

    # def get_full_address(self):
    #     district = self.get_district()
    #     return district.full_name + self.geo_label
    #
    # def get_district_label(self):
    #     import re
    #     district = self.get_district()
    #     return re.sub(
    #         r'(?:地区|区|自治州|市郊县|盟|市市辖区|市|省|特別行政區|自治州)$',
    #         '',
    #         district.name
    #     ) if district else ''

    # def distance(self):
    #     """ 获取这个对象离当前登录用户的地理距离，单位是公米 """
    #     request = get_request()
    #     if not hasattr(request.user, 'customer'):
    #         return None
    #     return self.distance_to(request.user.customer)

    # def distance_to(self, item):
    #     """ 获取当前对象到另一个 GeoPositionedModel 对象的距离
    #     :param item:
    #     :return:
    #     """
    #     return u.earth_distance(
    #         item.geo_lat,
    #         item.geo_lng,
    #         self.geo_lat,
    #         self.geo_lng
    #     )

    @staticmethod
    def annotate_distance_from(qs, lat, lng, field_name='distance'):
        """ 将 queryset 附加一个字段名
        :param qs: 原始 queryset
        :param lat: 参考点的纬度坐标
        :param lng: 参考点的经度坐标
        :param field_name: 附加到对象上的距离字段
        :return: 返回按照对指定坐标点距离从近到远排序的 queryset
        """
        return qs.extra(select={field_name: """{R} * acos(
            sin(radians({lat})) * sin(radians(geo_lat)) +
            cos(radians({lat})) * cos(radians(geo_lat)) * cos(radians({lng}-geo_lng))
        )""".format(R=GeoPositionedModel.EARTH_RADIUS, lat=lat, lng=lng)})

    @staticmethod
    def filter_by_distance(qs, lat, lng, distance, exclude=False):
        """ 根据距离筛选 QuerySet
        :param qs: 原始 queryset
        :param lat: 参考点的纬度坐标
        :param lng: 参考点的经度坐标
        :param distance: 基准距离
        :param exclude: 如果是 False（默认），返回距离小于基准距离的集合
        如果为 True，则返回距离大于基准距离的集合
        :return:
        """
        # 社区公告计算筛选范围
        return qs.extra(where=[
            """{R} * acos(
                sin(radians({lat})) * sin(radians(geo_lat)) +
                cos(radians({lat})) * cos(radians(geo_lat)) * cos(radians({lng}-geo_lng))
            ) {op} {distance}""".format(
                R=GeoPositionedModel.EARTH_RADIUS,
                lat=lat,
                lng=lng,
                distance=distance,
                op='>' if exclude else '<'
            )
        ])
