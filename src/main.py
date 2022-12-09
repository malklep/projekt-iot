from config import Config
import asyncio
from agent import Agent
from asyncua import Client

async def main():
    config = Config('config.ini')

    agents = []
    async with Client(config.server_url) as client:
        objects = client.get_node('i=85')

        for child in await objects.get_children():
            child_name = await child.read_browse_name()
            if child_name.Name != 'Server':
                connection_string = config.get_device_config(child_name.Name)
                agents.append(Agent.init(device = child, connection_string = connection_string))

        print(agents)
    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())