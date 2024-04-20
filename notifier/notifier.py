import random
from typing import Optional

import discord
import pandas as pd
from discord import app_commands

from secret import TOKEN

MY_GUILD = discord.Object(id=1046387245982175262)
CHANNEL_ID = 1046387247336923176


class ObstacleNotifier(discord.Client):
    """Discord bot that receives information about obstacles on the water surface and notifies the users about them.
    It is used as prevention of flooding and other water-related disasters.
    """

    def __init__(self, intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def notify_about_obstacle(self, info: dict, channel: discord.abc.Messageable, mention_everyone=False):
        """Notifies the users about the obstacle on the water surface.

        Args:
            info (dict): Information about the obstacle:
                - location (tuple(float, float)): Latitude and longitude of the obstacle
                - weather (str): Weather conditions
                - water_flow (float): Water flow conditions

        Returns:
            tuple: Tuple of (bool, str) where the first element is True if the notification was successful and False otherwise, and the second element is the response message
        """
        print(f'Notifying about obstacle at {info["location"]} in {channel}')
        message_to_send = f'Obstacle detected at {info["location"]}! Weather conditions: {info["weather"]}, water flow conditions: {info["water_flow"]}'
        if mention_everyone:
            message_to_send = '@everyone ' + message_to_send

        try:
            message = await channel.send(message_to_send)
        except discord.errors.Forbidden:
            return (False, f'Failed to send message to {channel.name}')
        return (True, f'Message {message} sent to {channel.name}')



intents = discord.Intents.default()



client = ObstacleNotifier(intents=intents)



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    channel = client.get_channel(CHANNEL_ID)



async def command_error(interaction, error):
    print(error)
    if isinstance(error, app_commands.errors.MissingAnyRole):
        await interaction.response.send_message(f'You are not allowed to use this command!', ephemeral=True)
    else:
        await interaction.response.send_message(f'Error: {error}', ephemeral=True)

client.run(TOKEN)
