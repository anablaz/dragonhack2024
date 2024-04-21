from collections import defaultdict

import discord
import numpy as np
import openmeteo_requests
import pandas as pd
import requests_cache
from discord import app_commands
from notifier import ObstacleNotifier
from retry_requests import retry
from secret import TOKEN

CHANNEL_ID = 1046387247336923176


intents = discord.Intents.default()


client = ObstacleNotifier(intents=intents)


async def run_weather(latitudes: list, longitudes: list):
    """Calls the Open-Meteo API to get the weather data for the given coordinates.

    Args:
        latitudes (list): List of latitudes (floats) to get the weather data for
        longitudes (list): List of longitudes (floats) to get the weather data for
    Returns:
        list: List of weather data values:
            - lat (float): Latitude of the measurement
            - lon (float): Longitude of the measurement
            - rain_ratio (float): Ratio of precipitation in next week to the precipitation in the last month
            - flow_ratio (float): Ratio of water flow in next week to the water flow in the last month
    """
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    flow_url = "https://flood-api.open-meteo.com/v1/flood"

    flow_params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "daily": "river_discharge",
        "past_days": 31,
        "forecast_days": 7
    }

    rain_url = "https://api.open-meteo.com/v1/forecast"
    rain_params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "daily": "precipitation_sum",
        "past_days": 31,
        "forecast_days": 7
    }

    flow_responses = openmeteo.weather_api(flow_url, params=flow_params)
    rain_responses = openmeteo.weather_api(rain_url, params=rain_params)
    results = []

    for flow_response, rain_response in zip(flow_responses, rain_responses):
        lat = rain_response.Latitude()
        lon = rain_response.Longitude()
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

        results.append({
            'lat': lat,
            'lon': lon,
            'rain_ratio': rain_ratio,
            'flow_ratio': flow_ratio
        })
    return results


async def evaluate_severity(lat, lon, size):
    """Evaluates the severity of the obstacle based on the location and size.

    Args:
        lat (float): Latitude of the obstacle
        lon (float): Longitude of the obstacle
        size (float): Size of the obstacle

    Returns:
        str: Severity of the obstacle
    """
    if size < 5:
        return 'low'
    elif size < 10:
        # get weather data
        weather_data = await run_weather([lat], [lon])
        rain_ratio = weather_data[0]['rain_ratio']
        flow_ratio = weather_data[0]['flow_ratio']
        if rain_ratio <= 1.5 or flow_ratio <= 1.2:
            return 'medium'
    return 'high'


async def run_preventive_weather_check():
    """Runs the preventive weather check.

    Returns:
        dict: Dictionary with the danger data in GeoJSON format
    """
    coordinates = pd.read_csv('coordinates.csv')
    river_names = coordinates['River'].tolist()
    latitudes = coordinates['Latitude'].tolist()
    longitudes = coordinates['Longitude'].tolist()
    weather_data = await run_weather(latitudes, longitudes)
    danger_data = {
        'type': 'FeatureCollection',
        'features': []
    }
    for river_name, data in zip(river_names, weather_data):
        if data['rain_ratio'] > 1.5 or data['flow_ratio'] > 1.2:
            danger_data['features'].append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [data['lon'], data['lat']]
                },
                'properties': {
                    'name': river_name,
                    'rain_ratio': data['rain_ratio'],
                    'flow_ratio': data['flow_ratio']
                }
            })
    return danger_data


async def run_classifier():
    """Runs the classifier to find obstacles, then check severity with weather data.

    Returns:
        dict: Dictionary with the classifier data in GeoJSON format
    """
    # TODO run our classifier here
    classifier_data = [{
        'location': (45.0, 45.0),
        'size': 6.0,
    }]
    obstacles_data = {
        'type': 'FeatureCollection',
        'features': []
    }
    for obstacle in classifier_data:
        lat, lon = obstacle['location']
        size = obstacle['size']
        severity = await evaluate_severity(lat, lon, size)
        if severity in ('medium', 'high'):
            weather_data = await run_weather([lat], [lon])
            await client.notify_about_obstacle(
                {
                    'location': (lat, lon),
                    'precipitation_ratio': weather_data[0]['rain_ratio'],
                    'water_flow_ratio': weather_data[0]['flow_ratio']

                },
                client.get_channel(CHANNEL_ID),
                mention_everyone=severity == 'high',
                prefix=':warning: *High severity obstacle detected* :warning:\n'
            )

        obstacles_data['features'].append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lon, lat]
            },
            'properties': {
                'severity': severity
            }
        })
    return obstacles_data


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    weather_data = await run_preventive_weather_check()
    obstacle_data = await run_classifier()


async def command_error(interaction, error):
    print(error)
    if isinstance(error, app_commands.errors.MissingAnyRole):
        await interaction.response.send_message(f'You are not allowed to use this command!', ephemeral=True)
    else:
        await interaction.response.send_message(f'Error: {error}', ephemeral=True)

client.run(TOKEN)