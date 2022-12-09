from azure.iot.device import IoTHubDeviceClient


class Agent:
  def __init__(self):
    self.device = None
    self.client = None
    self.connection_string = None

  @classmethod
  def init(cls, device, connection_string):
    agent = cls()
    agent.device = device
    agent.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    agent.client.connect()
    return agent