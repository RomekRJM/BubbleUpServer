import requests
from models import RegisteredClient
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from config import Config

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def fetch_geolocation_data(url, apikey, ip):
    response = requests.get('{}/{}/{}'.format(url, apikey, ip))

    if response.status_code == 200 and 'error' not in response.content:
        return response.json()

    return {}


def populate_location():
    cfg = Config()
    clients_wo_location = RegisteredClient.objects.filter(country__isnull=True)
    logger.info("Running scheduled task, to populate %s missing countries." % len(clients_wo_location))

    for client in clients_wo_location:
        geolocation = fetch_geolocation_data(cfg.get_config('geolocation-url'),
                                             cfg.get_config('geolocation-key'),
                                             client.ip)
        client.country = geolocation.get('countryName', 'Unknown')
        client.state = geolocation.get('stateProv', 'Unknown')
        client.city = geolocation.get('city', 'Unknown')
        client.save()

        logger.info("Found location for %s (%s/%s/%s)." % (client.ip, client.country, client.state, client.city))

    logger.info("Finished populating missing countries.")


@scheduler.scheduled_job('interval', seconds=3)
def schedule():
    populate_location()
