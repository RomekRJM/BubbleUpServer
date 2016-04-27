from rest_framework import serializers

from BubbleUpServer.models import RegisteredClient

__author__ = "roman.subik"


class RegisteredClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegisteredClient
        fields = ('uuid', 'date_joined')
