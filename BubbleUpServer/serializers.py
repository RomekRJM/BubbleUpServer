from rest_framework import serializers

from BubbleUpServer.models import RegisteredClient, Score

__author__ = "roman.subik"


class RegisteredClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegisteredClient
        fields = ('uuid', 'phrase', 'date_joined', 'country', 'ip')


class ScoreSerializer(serializers.ModelSerializer):

    registered_client = serializers.SlugRelatedField(many=False, read_only=True, slug_field='uuid')

    class Meta:
        model = Score
        fields = ('user_name', 'played_on', 'recieved_on', 'play_time', 'altitude', 'score', 'registered_client')
