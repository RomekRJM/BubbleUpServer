import uuid

# Create your views here.
from rest_framework import generics, mixins, viewsets
from rest_framework.response import Response

from BubbleUpServer.models import RegisteredClient
from BubbleUpServer.serializers import RegisteredClientSerializer
import datetime


class RegisteredClientViewSet(viewsets.ModelViewSet):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer


class RegisteredClientList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, format=None):
        serializer = RegisteredClientSerializer(data={
            "uuid": str(uuid.uuid4()),
            "date_joined": datetime.datetime.utcnow(),
            "ip": request.META['REMOTE_ADDR']
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class RegisteredClientDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'uuid'
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer

