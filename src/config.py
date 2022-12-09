import configparser

class Config:
  
  def __init__(self, config_file: str):
    self.config_file = config_file
    self.config = configparser.ConfigParser()
    self.load_config()

  def load_config(self):
    changes = False
    self.config.read(self.config_file)

    if not self.config.has_section('OPCUA'):
      self.config.add_section('OPCUA')
    
    if not self.config.has_section('DEVICES'):
      self.config.add_section('DEVICES')

    if not self.config.has_option('OPCUA', 'server_url'):
      self.config.set('OPCUA', 'server_url', input('Podaj adres serwera OPC-UA: '))
      changes = True

    if changes:
      self.save_config()

  @property
  def server_url(self):
    return self.config.get('OPCUA', 'server_url')

  def get_device_config(self, device_name: str):
    changes = False
    if not self.config.has_option('DEVICES', device_name):
      self.config.set('DEVICES', device_name, input(f'Podaj connection string dla {device_name}: '))
      changes = True

    if changes:
      self.save_config()
      
    return self.config.get('DEVICES', device_name)

  def save_config(self):
    with open(self.config_file, 'w') as configfile:
      self.config.write(configfile)
