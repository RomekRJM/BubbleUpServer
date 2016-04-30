from rest_framework import serializers

from BubbleUpServer.models import RegisteredClient, Score

__author__ = "roman.subik"


class RegisteredClientSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = RegisteredClient
        fields = ('uuid', 'phrase', 'date_joined', 'country', 'ip')


class ScoreSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Score
        fields = ('registered_client', 'user_name', 'played_on', 'recieved_on', 'play_time', 'altitude', 'score')
