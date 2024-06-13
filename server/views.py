import asyncio
import json
import requests
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from message.models import Messages, Groups, Group_participants
from django.db.models import Q
from message.serializers import MessageSerializer
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
import threading
from asgiref.sync import sync_to_async
# from utils.decorator import some_decorator
# from utils.auth import verify, hash
from django.db import transaction
from dotenv import load_dotenv
import os 
import uuid
from utils.file import validateFileType, generateUUIDForFile
from utils.custom_redis import redisInstance
from decorator.auth import verify
from utils.chat import createChatRoom, groupParticipantTransaction
from enums._enums import MessageStatus, GroupType
from time import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
logging.basicConfig(
        handlers=[RotatingFileHandler('logs/chat.log', maxBytes=1000000, backupCount=50)],
        level=logging.DEBUG,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt='%Y-%m-%dT%H:%M:%S')

# Load environment variables from .env file
load_dotenv()

@csrf_exempt
def addParticipantsToGroup(request, group_uuid):
    """
    ADD PARTICIPANTS TO GROUP
    """
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        try:
            body = json.loads(body_unicode)
            user1_uuid = body['user1_uuid']
            success = groupParticipantTransaction(user1_uuid, group_uuid)
            if success == 0:
                return JsonResponse({
                    "success": 0,
                    "message": f"Error"
                }, status=400)
            return JsonResponse({
                "success": 1,
                "message": "Success",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "success": 0,
                "message": f"Error, {str(e)}"
            }, status=400)

    
@sync_to_async
def init(user_uuid, LIMIT, offset):
    returnList=[]
    messages = Messages.objects.raw(f"""
        SELECT *, MAX(messages.timestamp) as last_post_date
        FROM `messages` 
        JOIN groups ON groups.uuid = messages.group_id 
        JOIN group_participants ON groups.uuid = group_participants.group_id
        JOIN (
        SELECT 
        content as t2content, 
        max(t2.timestamp) as t2stamp,
        COUNT(CASE WHEN t2.status = {MessageStatus.Received} THEN {MessageStatus.Received} END) as unread
        FROM messages as t2 
        JOIN groups as g2 ON g2.uuid = t2.group_id 
        JOIN group_participants as gp2 ON g2.uuid = gp2.group_id 
        WHERE gp2.user_id = '{user_uuid}'
        group by t2.group_id
        ) t2result
        WHERE group_participants.user_id = '{user_uuid}' and messages.timestamp = t2stamp
        GROUP BY groups.uuid 
        LIMIT {LIMIT} OFFSET {offset}
    """)
    for message in messages:
        print("message", message)
        is_online = checkOnline(message)
        returnList.append({
            "group_uuid": message.uuid,
            "last_post_date": message.last_post_date,
            "last_post": message.content,
            "unread": message.unread,
            "is_online": is_online
        })
    print("returnList", returnList)
    return returnList

# SELECT *, MAX(messages.timestamp) as last_post_date, COUNT(CASE WHEN messages.status = 1 THEN 1 END) as unread 
# FROM `messages` 
# JOIN groups ON groups.uuid = messages.group_id 
# JOIN group_participants ON groups.uuid = group_participants.group_id
# JOIN (
# SELECT content as t2content, max(t2.timestamp) as t2stamp FROM messages as t2 
# JOIN groups as g2 ON g2.uuid = t2.group_id 
# JOIN group_participants as gp2 ON g2.uuid = gp2.group_id 
# WHERE gp2.user_id = '5c7de3e98ce0492d9331d2700b46d3d2'
# group by t2.group_id
# ) t2result
# WHERE group_participants.user_id = '5c7de3e98ce0492d9331d2700b46d3d2' and messages.timestamp = t2stamp
# GROUP BY groups.uuid 
# LIMIT 10 OFFSET 0


# SELECT 
# content as t2content, 
# max(t2.timestamp) as t2stamp,
# COUNT(CASE WHEN t2.status = 1 THEN 1 END) as unread
# FROM messages as t2 
# JOIN groups as g2 ON g2.uuid = t2.group_id 
# JOIN group_participants as gp2 ON g2.uuid = gp2.group_id 
# WHERE gp2.user_id = '5c7de3e98ce0492d9331d2700b46d3d2'
# group by t2.group_id


# SELECT *, MAX(messages.timestamp) as last_post_date, COUNT(CASE WHEN messages.status = 1 THEN 1 END) as unread 
# FROM `messages` 
# JOIN groups ON groups.uuid = messages.group_id 
# JOIN group_participants ON groups.uuid = group_participants.group_id 
# WHERE user_id = '5c7de3e98ce0492d9331d2700b46d3d2'
# GROUP BY groups.uuid 
# LIMIT 10 OFFSET 0

# SELECT *, COUNT(CASE WHEN messages.status = 1 THEN 1 END) as unread
# FROM messages AS messages,
# (select MAX(timestamp) as last_post_date FROM messages GROUP BY group_id) AS max_time
# JOIN groups JOIN group_participants
# WHERE group_participants.user_id = '5c7de3e98ce0492d9331d2700b46d3d2' and status = 1 and messages.timestamp=last_post_date
# LIMIT 10 OFFSET 0

def checkOnline(message):
    # check redis whether user is online
    if message.type == GroupType.OneToOne:
        group_participants = Group_participants.objects.filter(group_id=str(message.group_id).replace('-', ''))
        for participant in group_participants:
            if participant.user_id is not message.sender_id:
                return redisInstance.hget("online", str(participant.user_id).replace('-', ''))
    return None

@csrf_exempt
def notification(request, user_uuid, offset):
    """
    Returns the intial data for user. Initial Data should include 10 groups (with pagination) and their last message
    order by last message date
    """
    LIMIT = 10
    if request.method == "GET":
        async def event_stream():
            while True:
                returnList = []
                try:
                    returnList = await init(user_uuid, LIMIT, offset)
                except Exception as e:
                    yield f'data: Error, {e} \n\n'

                yield f'data: {returnList} \n\n'
                await asyncio.sleep(1)

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    

@csrf_exempt
# @verify
def getOrSetGroup(request):
    """
    Gets the UUID of the chat if exists, if not creates the chat room
    """
    if request.method == "POST":
        try:
            user1_uuid = request.POST.get('user1_uuid')
            user2_uuid = request.POST.get('user2_uuid')

            # CHECK IF CHAT GROUP ALREADY CREATED
            group = Groups.objects.filter(type=GroupType.OneToOne).filter(group_participants__user_id=user1_uuid).filter(group_participants__user_id=user2_uuid).distinct()

            if group.count() == 0:
                success = createChatRoom(user1_uuid, user2_uuid)
                if success['success'] == 0:
                    return JsonResponse({
                    "success": 0,
                    "message": "Error"
                }, status=400)
            return JsonResponse({
                "success": 1,
                "message": "Success",
                "group": str(group.first().uuid) if group.count() > 0 else success['group_uuid']
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "success": 0,
                "message": f"Error, {str(e)}"
            }, status=400)


@csrf_exempt
def message(request, group_uuid):
    """
    Handles the function when user send a message to the server
    """
    if request.method == "POST":
        
        text = request.POST.get('text')
        user1_uuid = request.POST.get('user1_uuid')
        file = request.FILES.get('file')

        # CHECK FILE TYPE, MINE TYPE, FILE VALIDATION
        if file is not None:
            success = validateFileType(file.name, file.content_type)
            if success == False:
                return JsonResponse({
                    "success": 0,
                    "message": "Error, file type not supported"
                }, status=400)
            file.name = generateUUIDForFile(file.name)
        # CHECK IF GROUP EXISTS , IF GROUP DOESNT EXISTS, WILL CRASH, ADD TRY CATCH BLOCK
        try:
            group = Groups.objects.get(uuid=group_uuid)
        except Exception as e:
            return JsonResponse({
                "success": 0,
                "message": "Error, group does not exist"
            }, status=400)

        # CHECK IF USER ID IS IN ONE OF THE user_ids
        user_exists = False
        for participants in group.group_participants_set.all():
            if str(participants.user_id).replace('-', '') == user1_uuid:
                user_exists = True
                break

        if user_exists == False:
            return JsonResponse({
                "success": 0,
                "message": "User does not exist in this chat"
            }, status=400)

        message = Messages(content=text, sender_id=user1_uuid, group_id=group_uuid, status=MessageStatus.Received, file=file)
        message.save()
        return JsonResponse({
            "success": 1,
            "message": "successfully sent"
        }, status=200)
    
@sync_to_async
def getGroupParticipants(group_uuid):
    # GET THE GROUP PARTICIPANTS, LOOP THROUGH IT AND CHECK REDIS WHETHER USER HAS KEY DOWN
    typing_participants = []
    group_participants = Group_participants.objects.filter(group_id=group_uuid).all()
    for group_participant in group_participants:
        user = str(group_participant.user_id).replace("-", "")
        is_typing = redisInstance.hget("typing", f"{group_uuid}_{user}")
        if is_typing:
            typing_participants.append(str(group_participants.user_id))
    return typing_participants

@sync_to_async
def getLatestMessage(group_uuid, user_id):
    # IF MESSAGE STATUS IS NOT SEEN, CHECK IF ANOTHER USER IS STREAMING, IF YES, UPDATE STATUS TO SEEN
    messages = Messages.objects.filter(group_id=group_uuid).all().order_by('-id')[:10]
    output = []
    print("messages", messages)
    for message in messages:
        if message.status != MessageStatus.Seen:
            group = message.group
            if group.type == GroupType.OneToOne and str(message.sender_id).replace('-', '') != user_id:
                message.status = int(MessageStatus.Seen)
                #message.save()
    
        output.append({
            "message": message.content,
            "status": message.status,
            "timestamp": message.timestamp
        })
    return output

async def stream(request):
    """
    Sends server-sent events to the client.
    """
    user_id = request.GET.get("user_id")
    group_uuid = request.GET.get("group_uuid")
    async def event_stream():
        while True:
            typing_participants = await getGroupParticipants(group_uuid)
            messages = await getLatestMessage(group_uuid, user_id)

            # async for message in Messages.objects.filter(group_id=group_uuid).all().order_by('-id')[:10]:
            #     # IF MESSAGE STATUS IS NOT SEEN, CHECK IF ANOTHER USER IS STREAMING, IF YES, UPDATE STATUS TO SEEN
            #     if message.status != MessageStatus.Seen:
            #         getGroupType = sync_to_async(lambda e: e.group, thread_sensitive=True)
            #         group = await getGroupType(message)
            #         if group.type == GroupType.OneToOne and str(message.sender_id).replace('-', '') != user_id:
            #             message.status = int(MessageStatus.Seen)
            #             save = sync_to_async(lambda message: message.save(), thread_sensitive=True)
            #             await save(message)
                    
            #     messages.append({
            #         "message": message.content,
            #         "status": message.status,
            #         "timestamp": message.timestamp
            #     })
            output = {
                "messages": messages,
                "typing": typing_participants
            }


            yield f'data: {output} \n\n'
            await asyncio.sleep(1)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

async def typing(request, group_uuid, user_id):
    """
    Add user to the list of users currently typing 
    """
    redisInstance.hset("typing", f"{group_uuid}_{user_id}", True, 5)
    hget = redisInstance.hget("typing", f"{group_uuid}_{user_id}")
    return HttpResponse(hget)


async def online(request, user):
    """
    Add user to the list of users currently online 
    """
    print("user", user)
    redisInstance.hset("online", user, True, 120)
    hget = redisInstance.hget("online", user)
    return HttpResponse(hget)

async def test(request):
    async for e in Messages.objects.filter(group_id='4c64a417f02e496b8674842060d1673c').all().order_by('-id')[:10]:
        print("e", e)
        getGroupType = sync_to_async(lambda e: e.group, thread_sensitive=True)
        group = await getGroupType(e)
        print(group.type)
        if group.type == GroupType.OneToOne:
            pass

    return HttpResponse(1)

async def redis_get(request, hash, key):
    hget = redisInstance.hget(hash, key)
    return HttpResponse(hget)