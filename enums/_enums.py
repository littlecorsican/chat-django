
from enum import Enum, auto, IntEnum
 
class GroupType(IntEnum):
    OneToOne = 0
    GroupChat = 1

class MessageStatus(IntEnum):
    Sent = 0
    Received = 1
    Seen = 2