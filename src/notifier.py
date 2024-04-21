import random
from typing import Optional

import discord
import pandas as pd
from discord import app_commands

MY_GUILD = discord.Object(id=1046387245982175262)


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

    async def notify_about_obstacle(self, info: dict, channel: discord.abc.Messageable, mention_everyone=False, prefix=''):
        """Notifies the users about the obstacle on the water surface.

        Args:
            info (dict): Information about the obstacle:
                - location (tuple(float, float)): Latitude and longitude of the obstacle
                - precipitation_ratio (float): Ratio of precipitation in next week to the precipitation in the last month
                - water_flow_ratio (float): Ratio of water flow in next week to the water flow in the last month

        Returns:
            tuple: Tuple of (bool, str) where the first element is True if the notification was successful and False otherwise, and the second element is the response message
        """
        print(f'Notifying about obstacle at {info["location"]} in {channel}')
        message_to_send = f'{prefix} Obstacle detected at {info["location"]}!\nPrecipitation for next week vs. last month: {info["precipitation_ratio"]:.2f}.\nWater flow conditions for next week vs. last month: {info["water_flow_ratio"]:.2f}.'.strip()
        if mention_everyone:
            message_to_send = '@everyone ' + message_to_send

        try:
            message = await channel.send(message_to_send)
        except discord.errors.Forbidden:
            return (False, f'Failed to send message to {channel.name}')
        return (True, f'Message {message} sent to {channel.name}')
