from rest_framework import serializers
from . import models as m


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Option
        fields = '__all__'


