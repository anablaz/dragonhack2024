from notifier import ObstacleNotifier

import discord
from discord import app_commands
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import numpy as np
from collections import defaultdict



CHANNEL_ID = 1046387247336923176



from secret import TOKEN


intents = discord.Intents.default()


client = ObstacleNotifier(intents=intents)


async def run_weather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    flow_url = "https://flood-api.open-meteo.com/v1/flood"
    top_north = 46.1536981
    top_south = 45.421944
    top_east = 16.610556
    top_west = 13.375556
    lat_range = np.linspace(top_north, top_south, 10)
    lon_range = np.linspace(top_east, top_west, 10)
        
    flow_params = {
        "latitude": lat_range,
        "longitude": lon_range,
        "daily": "river_discharge",
        "past_days": 31,
        "forecast_days": 7
    }

    rain_url = "https://api.open-meteo.com/v1/forecast"
    rain_params = {
        "latitude": lat_range,
        "longitude": lon_range,
        "daily": "precipitation_sum",
        "past_days": 31,
        "forecast_days": 7
    }

    flow_responses = openmeteo.weather_api(flow_url, params=flow_params)
    rain_responses = openmeteo.weather_api(rain_url, params=rain_params)
    responses = zip(flow_responses, rain_responses)

    for flow_response, rain_response in responses:
        lat = np.round(rain_response.Latitude(), 3)
        lon = np.round(rain_response.Longitude(), 3)
        print(f"Coordinates {lat}°N {lon}°E")

        flow_daily = flow_response.Daily()
        daily_river_discharge = flow_daily.Variables(0).ValuesAsNumpy()
        mean_flow_last_month = daily_river_discharge[:-7].mean()
        mean_flow_next_week = daily_river_discharge[-7:].mean()
        flow_ratio = np.round(mean_flow_next_week / mean_flow_last_month, 2)

        rain_daily = rain_response.Daily()
        daily_precipitation_sum = rain_daily.Variables(0).ValuesAsNumpy()
        mean_rain_last_month = daily_precipitation_sum[:-7].mean()
        mean_rain_next_week = daily_precipitation_sum[-7:].mean()
        rain_ratio = np.round(mean_rain_next_week / mean_rain_last_month, 2)


        if any(np.isnan([mean_flow_last_month, mean_flow_next_week, mean_rain_last_month, mean_rain_next_week])):
            print("Warning: Some values are NaN")
            continue

        channel = client.get_channel(CHANNEL_ID)
        print(f'rain ratio: {rain_ratio}, flow ratio: {flow_ratio}')

        if rain_ratio > 1.5:
            print("Warning: High precipitation forecast")
            await client.notify_about_obstacle({'location': (lat, lon), 'precipitation_ratio': rain_ratio, 'water_flow_ratio': flow_ratio}, channel, mention_everyone=False)
        elif flow_ratio > 1.5:
            print("Warning: High discharge forecast")
            await client.notify_about_obstacle({'location': (lat, lon), 'precipitation_ratio': rain_ratio, 'water_flow_ratio': flow_ratio}, channel, mention_everyone=False)



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await run_weather()



    # await client.notify_about_obstacle({'location': (45.0, 45.0), 'weather': 'rainy', 'water_flow': 0.5}, channel, mention_everyone=True)


async def command_error(interaction, error):
    print(error)
    if isinstance(error, app_commands.errors.MissingAnyRole):
        await interaction.response.send_message(f'You are not allowed to use this command!', ephemeral=True)
    else:
        await interaction.response.send_message(f'Error: {error}', ephemeral=True)

client.run(TOKEN)
