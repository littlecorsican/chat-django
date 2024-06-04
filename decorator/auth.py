from django.http import HttpResponse, JsonResponse
from utils.auth import verify_mc, hash
import json

def verify(func):
    def verify_inner(request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        mc = request.headers.get("Authorization")
        print("mc", mc)
        user1_uuid = body['user1_uuid']
        auth = verify_mc(user1_uuid, mc)
        if auth == False:
            return HttpResponse('Unauthorized', status=401)

        print("auth", auth)
        return func(request)
    return verify_inner