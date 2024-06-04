import hashlib
import requests
import os
import uuid

def hash(appid, access_token, uid, uid2):

    modi_data = f'uid={uid}&uid2={uid2}'
    str_target = '%s%s%s'%(modi_data, access_token, appid)
    md = hashlib.sha256()
    str_target = str_target.upper()
    md.update(str_target.encode('utf-8'))
    mc = md.hexdigest()
    mc = mc.upper()
    return mc

def verify_mc(uid, mc):
    BASE_HOST = os.getenv('BASE_HOST')
    request=requests.post(
        f'{BASE_HOST}/webapi/chat/verify/',
        data={
            "appid": os.getenv('APPID'),
            "uid": uid,
            "mc": mc,
        },
    )
    #response = request.json()
    if request.status_code == 200:
        return True
    return False

def generateUUID():
    uuid_new = str(uuid.uuid4())
    print("uuid_new", uuid_new)
    return uuid_new      