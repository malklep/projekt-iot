from enum import Enum
from asyncua.ua import Variant


class DeviceProperty(Enum):
    ProductionStatus = "ProductionStatus"
    WorkorderId = "WorkorderId"
    ProductionRate = "ProductionRate"
    GoodCount = "GoodCount"
    BadCount = "BadCount"
    Temperature = "Temperature"
    DeviceError = "DeviceError"


class DeviceMethod(Enum):
    EmergencyStop = "EmergencyStop"
    ResetErrorStatus = "ResetErrorStatus"


class DeviceError(Enum):
    EmergencyStop = 1
    PowerFailure = 2
    SensorFailure = 4
    Unknown = 8

    @classmethod
    def errors(cls, code: int):
        for e in cls:
            if code & e.value:
                yield e


class Device:
    def __init__(self, device, client):
        self.device = device
        self.client = client

    @property
    async def name(self):
        device_name = await self.device.read_browse_name()
        return device_name.Name

    @classmethod
    def init(cls, device, client):
        return cls(device, client)

    async def get_property_node(self, prop: DeviceProperty):
        return await self.device.get_child(f"0:{prop.value}")

    async def get_property_value(self, prop: DeviceProperty):
        node = await self.get_property_node(prop)
        return await node.read_value()

    async def set_property_value(self, prop: DeviceProperty, value: Variant):
        node = await self.get_property_node(prop)
        await node.write_value(value)

    async def call_method(self, prop: DeviceMethod):
        await self.device.call_method(prop.value)
