import uuid

from django.http import HttpResponse, Http404
from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from BubbleUpServer.models import RegisteredClient
from BubbleUpServer.serializers import RegisteredClientSerializer
import datetime


class RegisteredClientViewSet(viewsets.ModelViewSet):
    queryset = RegisteredClient.objects.all()
    serializer_class = RegisteredClientSerializer


class JSONResponse(HttpResponse):

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def registeredclient_list(request):
    if request.method == 'GET':
        registered_client = RegisteredClient.objects.all()
        serializer = RegisteredClientSerializer(registered_client, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        serializer = RegisteredClientSerializer(data={
            "uuid": str(uuid.uuid4()),
            "date_joined": datetime.datetime.utcnow(),
            "ip": request.META['REMOTE_ADDR']
        })
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def registered_client_detail(request, uuid):
    try:
        registered_client = RegisteredClient.objects.get(uuid__exact=uuid)
    except RegisteredClient.DoesNotExist:
        return JSONResponse({"status": "not_found"}, status=404)

    if request.method == 'GET':
        serializer = RegisteredClientSerializer(registered_client)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = RegisteredClientSerializer(registered_client, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        registered_client.delete()
        return JSONResponse({"status": "deleted"}, status=204)


class RegisteredClientList(APIView):
    def get(self, request, format=None):
        registered_client = RegisteredClient.objects.all()
        serializer = RegisteredClientSerializer(registered_client, many=True)
        return JSONResponse(serializer.data)

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
    def get_object(self, pk):
        try:
            registered_client = RegisteredClient.objects.get(uuid__exact=uuid)
        except RegisteredClient.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        registered_client = self.get_object(pk)
        serializer = RegisteredClientSerializer(registered_client)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        registered_client = self.get_object(pk)
        serializer = RegisteredClientSerializer(registered_client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Response(serializer.data)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        registered_client = self.get_object(pk)
        registered_client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

