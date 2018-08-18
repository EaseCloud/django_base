from django.db import models


class Image(models.Model):
    """ 图片
    TODO: 考虑支持七牛引擎的问题
    TODO: 还要考虑裁剪缩略图的问题
    TODO: 存放的路径要按照 md5sum 折叠，以节省空间
    """

    name = models.CharField(
        verbose_name='图片名称',
        max_length=255,
        blank=True,
        default='',
    )

    image = models.ImageField(
        verbose_name='图片',
        upload_to='images/',
        null=False,
        blank=True,
    )

    ext_url = models.URLField(
        verbose_name='外部图片链接',
        blank=True,
        null=False,
        default='',
    )

    class Meta:
        verbose_name = '图片'
        verbose_name_plural = '图片'
        db_table = 'base_media_image'

    def url(self):
        return self.image.url if self.image else self.ext_url

    def __str__(self):
        return self.name

    @staticmethod
    def from_file(file):
        """ TODO: 工厂方法
        根据提交的 file 构造一个 ImageModel 对象
        如果存在相同的 md5sum
        :return:
        """

    @staticmethod
    def from_url_reference(url):
        """ 工厂方法
        根据指定的 url 生成一个引用 ImageModel
        :return:
        """
        return Image.objects.create(ext_url=url, name=url.split('/')[-1])

    @staticmethod
    def from_url_download(url):
        """ TODO: 工厂方法
        根据指定的 url 下载图片保存，生成一个 ImageModel
        :return:
        """

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.image.name
        super().save(*args, **kwargs)


class GalleryModel(models.Model):
    images = models.ManyToManyField(
        verbose_name='图片',
        to='Image',
        related_name='%(class)ss_attached',
        blank=True,
    )

    class Meta:
        abstract = True
