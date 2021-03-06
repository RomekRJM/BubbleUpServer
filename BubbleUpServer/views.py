import uuid

from rest_framework import generics, mixins, viewsets, exceptions
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone

from BubbleUpServer.config import Config
from BubbleUpServer.models import RegisteredClient, Score
from BubbleUpServer.phrases import Phrase
from BubbleUpServer.serializers import RegisteredClientSerializer, ScoreSerializer, ScorePagination


def has_valid_phrase(func):
    def func_wrapper(*args, **kwargs):

        if ('phrase' not in args[1].data) or (not Phrase().matches(args[1].data['phrase'])):
            return HttpResponse('Unauthorized', status=401)

        return func(*args, **kwargs)
    return func_wrapper


class RegisteredClientViewSet(viewsets.ModelViewSet):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer


class RegisteredClientList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @has_valid_phrase
    def post(self, request, format=None):

        if "user_name" not in request.data or "phrase" not in request.data:
            return Response(status=400)

        client_host_header = Config().get_config("client-host-header")

        serializer = RegisteredClientSerializer(data={
            "uuid": str(uuid.uuid4()),
            "user_name": request.data['user_name'],
            "date_joined": timezone.now(),
            "ip": request.META[client_host_header],
            "phrase": request.data['phrase']
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class RegisteredClientDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'uuid'
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer


class ScoreList(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer
    pagination_class = ScorePagination

    def get_queryset(self):
        order_by = ['-score', 'played_on']
        if 'order_by' in self.request.query_params:
            if self.request.query_params['order_by'] == 'altitude':
                order_by = ['-altitude', 'play_time', 'played_on']

        if 'uuid' in self.kwargs:
            registered_client = RegisteredClient.objects.filter(uuid=self.kwargs['uuid'])

            if registered_client.count() > 0:
                return Score.objects.filter(registered_client_id=registered_client[0].id).order_by(*order_by)
            else:
                raise exceptions.NotFound('Client with uuid ' + self.kwargs['uuid'] + ' was not found on the server.')

        return Score.objects.all().order_by(*order_by)
