from django.db import transaction
from message.models import Messages, Groups, Group_participants
from django.db.models import Q

@transaction.atomic
def createChatRoom(user1_uuid, user2_uuid):
    try:
        group = Groups.objects.create()
        user1 = Group_participants.objects.create(user_id=user1_uuid, group_id=group.uuid)
        user2 = Group_participants.objects.create(user_id=user2_uuid, group_id=group.uuid)
        return {
            "success": 1,
            "group_uuid": str(group.uuid)
        }
    except Exception as e:
        print(str(e))
        return {
            "success": 0,
            "group_uuid": ""
        }
    

@transaction.atomic
def groupParticipantTransaction(user1_uuid, group_uuid):
    try:
        # CONVERT GROUP FROM 2-PEOPLE GROUP TO MULTI-PEOPLE GROUP
        group = Groups.objects.get(uuid=group_uuid)
        print("group", group)
        group.type = 1
        group.save()

        # ADD MORE PARTICIPANTS TO GROUP PARTICIPANTS TABLE
        group_participants = Group_participants(user_id=user1_uuid,group_id=group_uuid)
        group_participants.save()

        return 1
    except Exception as e:
        print(str(e))
        return 0
    