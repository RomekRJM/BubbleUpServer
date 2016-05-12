from rest_framework import serializers

from BubbleUpServer.models import RegisteredClient, Score

import datetime

__author__ = "roman.subik"


class RegisteredClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RegisteredClient
        fields = ('uuid', 'user_name', 'phrase', 'date_joined', 'country', 'ip')


class ScoreSerializer(serializers.ModelSerializer):

    registered_client = serializers.SlugRelatedField(many=False, read_only=False, slug_field='uuid', allow_null=True,
                                                     queryset=RegisteredClient.objects.all())
    recieved_on = serializers.StringRelatedField(required=False)

    class Meta:
        model = Score
        fields = ('played_on', 'recieved_on', 'play_time', 'altitude', 'score', 'registered_client')

    def create(self, validated_data):
        validated_data['recieved_on'] = datetime.datetime.utcnow()

        score = Score()
        score.registered_client = RegisteredClient.objects.get(uuid__exact=validated_data['registered_client'].uuid)
        score.played_on = validated_data['played_on']
        score.recieved_on = validated_data['recieved_on']
        score.play_time = validated_data['play_time']
        score.altitude = validated_data['altitude']
        score.score = validated_data['score']

        score.save()
        return score
