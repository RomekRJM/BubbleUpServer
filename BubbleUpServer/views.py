import uuid

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

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