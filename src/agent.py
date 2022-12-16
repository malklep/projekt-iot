import asyncio
from enum import Enum
from json import dumps
from datetime import datetime

from azure.iot.device import IoTHubDeviceClient, Message, MethodRequest, MethodResponse
from device import DeviceProperty, DeviceMethod, DeviceError
from asyncua.ua import Variant, VariantType


class MessageType(Enum):
    TELEMETRY = 'telemetry'
    EVENT = 'event'


class Agent:
    def __init__(self, device, connection_string):
        self.device = device
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
        self.client.connect()

        self.client.on_method_request_received = self.method_handler
        self.client.on_twin_desired_properties_patch_received = self.twin_update_handler

        self._tasks = []
        self._errors = []
        self.message_index = 0

    @property
    async def subscribed_properties(self):
        return [
            await self.device.get_property_node(DeviceProperty.ProductionRate),
            await self.device.get_property_node(DeviceProperty.DeviceError)
        ]

    @property
    def tasks(self):
        tasks = self._tasks.copy()
        tasks.append(self.send_telemetry())
        self._tasks.clear()
        return map(asyncio.create_task, tasks)

    @classmethod
    def init(cls, device, connection_string):
        return cls(device, connection_string)

    async def send_telemetry(self):
        data = {
            "ProductionStatus": await self.device.get_property_value(DeviceProperty.ProductionStatus),
            "WorkorderId": await self.device.get_property_value(DeviceProperty.WorkorderId),
            "GoodCount": await self.device.get_property_value(DeviceProperty.GoodCount),
            "BadCount": await self.device.get_property_value(DeviceProperty.BadCount),
            "Temperature": await self.device.get_property_value(DeviceProperty.Temperature),
        }

        print(data)
        self.send_message(data, MessageType.TELEMETRY)

    def send_message(self, data, message_type: MessageType):
        message = Message(
            data=dumps(data),
            message_id=self.message_index,
            content_type='application/json',
            content_encoding='utf-8'
        )
        message.custom_properties['message_type'] = message_type.value
        self.client.send_message(message)

    def method_handler(self, method: MethodRequest):
        if method.name == "emergency_stop":
            print(f"Wywołano metodę: {method.name}")
            self._tasks.append(self.device.call_method(DeviceMethod.EmergencyStop))
        elif method.name == "reset_error_status":
            print(f"Wywołano metodę: {method.name}")
            self._tasks.append(self.device.call_method(DeviceMethod.ResetErrorStatus))
        elif method.name == "maintenance_done":
            print(f"Wywołano metodę: {method.name}")
            self.client.patch_twin_reported_properties({"last_maintenance_date": datetime.now().isoformat()})
        self.client.send_method_response(MethodResponse(method.request_id, 200))

    def twin_update_handler(self, data):
        if "production_rate" in data:
            print(f"Zmieniono wartość dla production_rate na: {data['production_rate']}")
            self._tasks.append(self.device.set_property_value(
                prop=DeviceProperty.ProductionRate,
                value=Variant(data["production_rate"], VariantType.Int32)
            ))

    # asyncua callback
    async def datachange_notification(self, node, val, _):
        name = await node.read_browse_name()
        print(f"Zmiana wartości {name.Name} dla {await self.device.name} na: {val}")
        if name.Name == DeviceProperty.DeviceError.value:
            errors = DeviceError.errors(val)
            for error in errors:
                if error not in self._errors:
                    self.client.patch_twin_reported_properties({"last_error_date": datetime.now().isoformat()})
                    self.send_message({"device_error": error.value}, MessageType.EVENT)

            self._errors = errors
            self.client.patch_twin_reported_properties({"device_error": val})
        elif name.Name == DeviceProperty.ProductionRate.value:
            self.client.patch_twin_reported_properties({"production_rate": val})

    def disconnect(self):
        self.client.disconnect()
