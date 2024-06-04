from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from message.models import Messages, Groups, Group_participants
from message.serializers import MessageSerializer, GroupSerializer, Group_participantSerializer
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
# Create your views here.

class MessagesViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for Messages
    """

    queryset = Messages.objects.all()

    @extend_schema(responses=MessageSerializer)
    def list(self, request): # /api/message/
        print("list")
        print("request", request)
        serializer = MessageSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs): # /api/message/
        print("request", request.data)
        print("request", args,  kwargs)
        serializer = MessageSerializer(data=request.data)
        print("serializer", serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        pass


    def retrieve(self, request, pk=None): # /api/message/2
        print("retrieve")
        print("request", request)
        print("self.queryset", type(self.queryset))
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = MessageSerializer(item)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        pass


class GroupsViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for Messages
    """

    queryset = Groups.objects.all()

    @extend_schema(responses=GroupSerializer)
    def list(self, request): # /api/message/
        print("list")
        print("request", request)
        serializer = GroupSerializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs): # /api/message/
        print("request", request.data)
        print("request", args,  kwargs)
        serializer = GroupSerializer(data=request.data)
        print("serializer", serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        pass


    def retrieve(self, request, pk=None): # /api/message/2
        print("retrieve")
        print("request", request)
        print("self.queryset", type(self.queryset))
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = GroupSerializer(item)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        pass