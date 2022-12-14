from azure.iot.device import IoTHubDeviceClient, Message
from enum import Enum
from json import dumps


class MessageType(Enum):
    TELEMETRY = 'telemetry'
    EVENT = 'event'


class Agent:
    def __init__(self):
        self.device = None
        self.client = None
        self.connection_string = None
        self.message_index = 0

    @classmethod
    def init(cls, device, connection_string):
        self = cls()
        self.device = device
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        self.client.connect()
        return self

    def send_message(self, data, message_type: MessageType):
        message = Message(
            data=dumps(data),
            message_id=self.message_index,
            content_type='application/json',
            content_encoding='utf-8'
        )
        message.custom_properties['message_type'] = message_type.value
        self.client.send_message(message)
