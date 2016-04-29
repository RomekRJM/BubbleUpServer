import uuid

from django.http import HttpResponse, Http404
from rest_framework.views import APIView

# Create your views here.
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from BubbleUpServer.models import RegisteredClient
from BubbleUpServer.serializers import RegisteredClientSerializer
import datetime


class RegisteredClientViewSet(viewsets.ModelViewSet):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer


class RegisteredClientList(APIView):
    def get(self, request, format=None):
        registered_client = RegisteredClient.objects.all()
        serializer = RegisteredClientSerializer(registered_client, many=True)
        return Response(serializer.data)

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


class RegisteredClientDetail(APIView):
    def get_object(self, uuid):
        try:
            return RegisteredClient.objects.get(uuid__exact=uuid)
        except RegisteredClient.DoesNotExist:
            raise Http404

    def get(self, request, uuid, format=None):
        registered_client = self.get_object(uuid)
        serializer = RegisteredClientSerializer(registered_client)
        return Response(serializer.data)

    def put(self, request, uuid, format=None):
        registered_client = self.get_object(uuid)
        serializer = RegisteredClientSerializer(registered_client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Response(serializer.data)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid, format=None):
        registered_client = self.get_object(uuid)
        registered_client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

