# from django.core.validators import FileExtensionValidator
# from upload_validator import FileTypeValidator
import uuid 
import time
import os

# CHECK EXTENSION AND MIME TYPE
def validateFileType(fileName, mime_type):
    allowedExtensions = ["pdf", "jpg", "jpeg", "png"]
    allowedMimeTypes = ["image/jpeg"]
    extension = fileName.split(".")[-1]

    print("mime_type", mime_type)
    if extension not in allowedExtensions:
        return False
    return True

    # validator = FileTypeValidator(
    #     allowed_types=['application/msword'],
    #     allowed_extensions=['.doc', '.docx']
    # )

    # file_resource = open(fileName)

    # # ValidationError will be raised in case of invalid type or extension
    # x = validator(file_resource)
    # print("x", x)


# 

def generateUUIDForFile(fileName):
    extension = fileName.split(".")[-1]
    return f"{uuid.uuid4()}.{extension}"