from rest_framework import serializers
from . import models as m


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Option
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    from ..base_media.serializers import AttachmentSerializer
    attachment_item = AttachmentSerializer(source='attachment', read_only=True)

    class Meta:
        model = m.Version
        fields = '__all__'
