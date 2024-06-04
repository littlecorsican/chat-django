from rest_framework import serializers
from .models import Messages, Groups, Group_participants
# from .models import Messages

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = "__all__"

class Group_participantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group_participants
        fields = "__all__"