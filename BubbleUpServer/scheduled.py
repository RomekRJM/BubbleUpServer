import requests
from models import RegisteredClient
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from config import Config

scheduler = BackgroundScheduler()
logging.basicConfig()


def fetch_geolocation_data(url, apikey, ip):
    response = requests.get('{}/{}/{}'.format(url, apikey, ip))

    if response.status_code == 200:
        return response.json()

    return {}


def populate_location():
    cfg = Config()
    clients_wo_location = RegisteredClient.objects.filter(country__isnull=True)

    for client in clients_wo_location:
        geolocation = fetch_geolocation_data(cfg.get_config('geolocation-url'),
                                             cfg.get_config('geolocation-key'),
                                             client.ip)
        client.country = geolocation.get('countryName', 'Unknown')
        client.state = geolocation.get('stateProv', 'Unknown')
        client.city = geolocation.get('city', 'Unknown')
        client.save()


@scheduler.scheduled_job('interval', seconds=3)
def schedule():
    if os.environ.get('TEST_MODE', 'off') != 'on':
        populate_location()
