from django.db import models
from django.utils import timezone
from uuid import uuid4
from django.core.validators import FileExtensionValidator

# Create your models here.

class Groups(models.Model):
    class Meta:
        db_table = "groups"
    uuid = models.UUIDField(primary_key = True, default=uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    type=models.IntegerField(null=False, default=0)

class Group_participants(models.Model):
    class Meta:
        db_table = "group_participants"
    group = models.ForeignKey(Groups, null=False, on_delete=models.CASCADE, default="")
    user_id = models.UUIDField(default=uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)

class Messages(models.Model):
    class Meta:
        db_table = "messages"
    content = models.TextField(default="")
    timestamp = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey(Groups, null=False, on_delete=models.CASCADE, default="")
    sender_id = models.UUIDField(default=uuid4, editable=False)
    status=models.CharField(max_length=25, default="")
    file=models.FileField(null=True, upload_to='',  validators=[FileExtensionValidator(allowed_extensions=['png'])])
