from django.core.paginator import InvalidPage
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.validators import UniqueValidator

from BubbleUpServer.models import RegisteredClient, Score
from django.db.models import Q, Max
from django.utils import six, timezone
from math import ceil

from BubbleUpServer.settings import REST_FRAMEWORK

__author__ = "roman.subik"


class RegisteredClientSerializer(serializers.ModelSerializer):
    user_name = UniqueValidator(queryset=RegisteredClient.objects.all())

    class Meta:
        model = RegisteredClient
        fields = ('uuid', 'user_name', 'phrase', 'date_joined', 'country', 'ip')


class ScoreSerializer(serializers.ModelSerializer):
    registered_client = serializers.SlugRelatedField(many=False, read_only=False, slug_field='uuid', allow_null=True,
                                                     queryset=RegisteredClient.objects.all())
    registered_client_name = serializers.ReadOnlyField(source='registered_client.user_name')
    recieved_on = serializers.StringRelatedField(required=False)

    class Meta:
        model = Score
        fields = ('played_on', 'recieved_on', 'play_time', 'altitude', 'score',
                  'registered_client', 'registered_client_name')

    def create(self, validated_data):
        validated_data['recieved_on'] = timezone.now()

        score = Score()
        score.registered_client = RegisteredClient.objects.get(uuid__exact=validated_data['registered_client'].uuid)
        score.played_on = validated_data['played_on']
        score.recieved_on = validated_data['recieved_on']
        score.play_time = validated_data['play_time']
        score.altitude = validated_data['altitude']
        score.score = validated_data['score']

        score.save()
        return score


class ScorePagination(PageNumberPagination):
    def __init__(self):
        self.page_number = 0

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = REST_FRAMEWORK['PAGE_SIZE']

        paginator = self.django_paginator_class(queryset, page_size)

        best_of = request.query_params.get('bestof', None)

        if best_of:
            order_by = request.query_params.get('order_by', None)
            better_scores = 0

            if order_by == 'score':
                best = Score.objects.filter(registered_client__uuid__exact=best_of).aggregate(Max('score'))
                top_score = Score.objects.filter(registered_client__uuid__exact=best_of, score=best['score__max']) \
                    .order_by('played_on')[0]
                better_scores = Score.objects.filter(Q(score__gt=top_score.score) |
                                                     (Q(score__exact=top_score.score) & Q(
                                                         played_on__lt=top_score.played_on))).count()
            elif order_by == 'altitude':
                best = Score.objects.filter(registered_client__uuid__exact=best_of).aggregate(Max('altitude'))
                top_altitude = Score.objects.filter(registered_client__uuid__exact=best_of) \
                    .filter(altitude__exact=best['altitude__max']).order_by('-play_time', 'played_on')[0]
                better_scores = Score.objects.filter(Q(altitude__gt=top_altitude.altitude) |
                                                     (Q(altitude=top_altitude.altitude) & Q(
                                                         play_time__lt=top_altitude.play_time)) |
                                                     (Q(altitude=top_altitude.altitude) & Q(
                                                         play_time=top_altitude.play_time) & Q(
                                                         played_on__lt=top_altitude.played_on))).count()

            self.page_number = int(ceil(float(better_scores + 1) / REST_FRAMEWORK['PAGE_SIZE']))

        else:
            self.page_number = request.query_params.get(self.page_query_param, 1)

        if self.page_number in self.last_page_strings:
            self.page_number = paginator.num_pages

        try:
            self.page = paginator.page(self.page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=self.page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)
