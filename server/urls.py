from django.urls import path
from . import views

urlpatterns = [
    path('api/message/<str:group_uuid>', views.message, name='message'),
    path('api/stream', views.stream, name='stream'),
    path('api/typing/<str:group_uuid>/<str:user_id>', views.typing, name='typing'),
    path('api/online/<str:user>', views.online, name='online'),
    path('api/group', views.getOrSetGroup, name='getOrSetGroup'),
    path('api/init/<str:user_uuid>/<int:offset>', views.init, name='init'),
    path('api/notification/<str:user_uuid>/<int:offset>', views.notification, name='notification'),
    path('api/groupparticipants/<str:group_uuid>', views.addParticipantsToGroup, name='addParticipantsToGroup'),
    path('api/test', views.test, name='test'),
    path('api/test2/<str:hash>/<str:key>', views.redis_get, name='redis_get'),
]