from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from BubbleUpServer.views import ScoreList
from models import RegisteredClient, Score
import random
import string
import time
import uuid
from datetime import datetime
from random import randint


def create_registeredclient():
    registered_client = RegisteredClient()
    registered_client.user_name = random_username()
    registered_client.country = 'Poland'
    registered_client.ip = '212.33.42.138'
    registered_client.date_joined = datetime.utcnow()
    registered_client.uuid = str(uuid.uuid4())
    registered_client.save()

    return registered_client


def create_score(registered_client):
    score = Score()
    score.registered_client = registered_client.id
    score.played_on = datetime.utcnow()
    score.recieved_on = datetime.utcnow()
    score.play_time = randint(200, 30000)
    score.altitude = randint(0, 2000)
    score.score = randint(0, 200)
    score.save()

    return score


def random_username():
    return "user-".join(random.choice(string.lowercase) for i in range(5))


class RegisteredClientTests(APITestCase):
    def test_get(self):
        registered_client = create_registeredclient()
        url = reverse('registered_client')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegisteredClient.objects.count(), 1)
        self.assertEqual(response.data['results'][0]['uuid'], registered_client.uuid)

    def test_post(self):
        url = reverse('registered_client')
        data = {
            "user_name": random_username(),
            "phrase": "nice wise ox"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("country", response.data)
        self.assertIn("ip", response.data)
        self.assertIn("date_joined", response.data)
        self.assertIn("uuid", response.data)
        self.assertIn("phrase", response.data)
        self.assertEqual(data["phrase"], response.data["phrase"])
        self.assertEqual(RegisteredClient.objects.count(), 1)

    def test_post_invalid_phrase(self):
        url = reverse('registered_client')
        data = {
            "user_name": random_username(),
            "phrase": "gibberish text here"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_post_to_short_phrase(self):
        url = reverse('registered_client')
        data = {
            "user_name": random_username(),
            "phrase": "nice wise"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_post_no_phrase(self):
        url = reverse('registered_client')
        data = {
            "user_name": random_username(),
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_post_no_username(self):
        url = reverse('registered_client')
        data = {
            "phrase": "nice wise ox"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_post_same_name_twice(self):
        url = reverse('registered_client')
        data = {
            "user_name": random_username(),
            "phrase": "nice wise ox"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RegisteredClient.objects.count(), 1)

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(RegisteredClient.objects.count(), 1)

    def test_put(self):
        registered_client = create_registeredclient()
        data = {
            "uuid": registered_client.uuid,
            "phrase": "nice wise ox",
            "date_joined": "2016-04-30T14:36:32.860402Z",
            "country": "Croatia",
            "ip": "127.0.0.1"
        }
        response = self.client.put('/registered_clients/' + registered_client.uuid + '/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegisteredClient.objects.count(), 1)
        self.assertEqual(str(response.data['country']), data['country'])

    def test_delete(self):
        registered_client = create_registeredclient()
        self.assertEqual(RegisteredClient.objects.count(), 1)

        response = self.client.delete('/registered_clients/' + registered_client.uuid + '/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_get_single(self):
        registered_client = create_registeredclient()
        response = self.client.get('/registered_clients/' + registered_client.uuid + '/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegisteredClient.objects.count(), 1)
        self.assertEqual(response.data['uuid'], registered_client.uuid)


def create_score(registered_client):
    score = Score()
    score.registered_client = registered_client
    score.played_on = datetime.utcnow()
    score.recieved_on = datetime.utcnow()
    score.play_time = random.randint(2000, 30000)
    score.altitude = random.randint(0, 2000)
    score.score = random.randint(0, 130)
    score.save()

    return score


def get_played_on_date_as_epoch(response, index):
    t = datetime.strptime(response.data['results'][index]['played_on'], '%Y-%m-%dT%H:%M:%S.%fZ').timetuple()
    return time.mktime(t) * 1000


def ordered_by_descending_playtime(response, num_of_elements):
    for i in range(1, num_of_elements):
        if response.data['results'][i-1]['play_time'] < response.data['results'][i]['play_time']:
            return False

    return True



class ScoreTests(APITestCase):
    def test_get(self):
        registered_client = create_registeredclient()
        create_score(registered_client)
        create_score(registered_client)
        response = self.client.get('/scores/registered_clients/' + registered_client.uuid + '/?order_by=play_time',
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Score.objects.count(), 2)
        self.assertEqual(response.data['results'][0]['registered_client'], registered_client.uuid)
        self.assertEqual(response.data['results'][1]['registered_client'], registered_client.uuid)

        self.assertTrue(get_played_on_date_as_epoch(response, 0) >= get_played_on_date_as_epoch(response, 1))

    def test_get_first_100_only(self):
        for i in range(120):
            create_score(create_registeredclient())

        response = self.client.get('/scores/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Score.objects.count(), 120)
        self.assertEqual(len(response.data['results']), ScoreList.MAX_ELEMENTS)

    def test_post(self):
        registered_client = create_registeredclient()
        data = {
            "played_on": "2016-05-01T22:22:14Z",
            "registered_client": registered_client.uuid,
            "play_time": 23400,
            "altitude": 555,
            "score": 127
        }
        response = self.client.post('/scores/registered_clients/' + registered_client.uuid + '/',
                                    data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(response.data['registered_client'], data['registered_client'])
        self.assertEqual(response.data['played_on'], data['played_on'])
        self.assertEqual(response.data['play_time'], data['play_time'])
        self.assertEqual(response.data['altitude'], data['altitude'])
        self.assertEqual(response.data['score'], data['score'])

    def test_scores_with_large_dataset(self):
        start = datetime.utcnow()
        clients = [create_registeredclient() for i in range(0, 1000)]
        after_clients = datetime.utcnow()

        print("Added clients in " + str(after_clients-start) + "s")

        for i in range(0, 100000):
            client = clients[randint(0, len(clients)-1)]
            create_score(client)

        after_scores = datetime.utcnow()
        print("Added scores in " + str(after_scores-after_clients) + "s")

        response = self.client.get('/scores/registered_clients/' + client.uuid + '/?order_by=play_time',
                                   format='json')

        scores_for_player = Score.objects.filter(registered_client_id__exact=client.id).count()

        assert ordered_by_descending_playtime(response, scores_for_player)

        after_response = datetime.utcnow()
        print("Got response in " + str(after_response-after_scores) + "s, for single client")

        response = self.client.get('/scores/?order_by=play_time',
                                   format='json')

        after_response_multi = datetime.utcnow()
        print("Got response in " + str(after_response_multi-after_response) + "s, for all clients")

        assert ordered_by_descending_playtime(response, ScoreList.MAX_ELEMENTS)
