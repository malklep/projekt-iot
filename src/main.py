from config import Config
import asyncio
from agent import Agent
from asyncua import Client
from device import Device


async def main():
    config = Config('config.ini')

    agents = []
    subscriptions = []

    async with Client(config.server_url) as client:
        objects = client.get_node('i=85')

        for child in await objects.get_children():
            child_name = await child.read_browse_name()
            if child_name.Name != 'Server':
                connection_string = config.get_device_config(child_name.Name)
                agent = Agent.init(
                    device=Device.init(device=child, client=client),
                    connection_string=connection_string
                )

                subscription = await client.create_subscription(500, agent)
                await subscription.subscribe_data_change(await agent.subscribed_properties)

                agents.append(agent)
                subscriptions.append(subscription)

        while True:
            for agent in agents:
                await asyncio.gather(*agent.tasks)
            await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
