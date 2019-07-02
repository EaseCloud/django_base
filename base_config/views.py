from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..base_utils import utils as u

from . import models as m
from . import serializers as s


class OptionViewSet(viewsets.GenericViewSet):
    queryset = m.Option.objects.all()
    serializer_class = s.OptionSerializer
    filter_fields = '__all__'

    @action(methods=['GET'], detail=False)
    def get_all(self, request):
        return Response(m.Option.get_all())

    @action(methods=['GET'], detail=False)
    def get(self, request):
        return Response(m.Option.get(request.query_params.get('key')))

    @action(methods=['POST'], detail=False)
    def set(self, request):
        m.Option.set(request.data.get('key'), request.data.get('value'))
        return u.response_success('设置成功', silent=True)
