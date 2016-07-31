from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from BubbleUpServer.serializers import ScorePagination
from models import RegisteredClient, Score
import random
import string
import time
import uuid
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import NotFound
from datetime import datetime, timedelta
from random import randint
from settings import REST_FRAMEWORK
from mock import Mock


def create_registeredclient():
    registered_client = RegisteredClient()
    registered_client.user_name = random_username()
    registered_client.country = 'Poland'
    registered_client.ip = '212.33.42.138'
    registered_client.date_joined = timezone.now()
    registered_client.uuid = str(uuid.uuid4())
    registered_client.save()

    return registered_client

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
    score.played_on = timezone.now()
    score.recieved_on = timezone.now()
    score.play_time = random.randint(2000, 30000)
    score.altitude = random.randint(0, 2000)
    score.score = random.randint(0, 130)
    score.save()

    return score


def get_played_on_date_as_epoch(response, index):
    t = datetime.strptime(response.data['results'][index]['played_on'], '%Y-%m-%dT%H:%M:%S.%fZ').timetuple()
    return time.mktime(t) * 1000


def assert_ordered_by_descending_altitude(response, num_of_elements):
    for i in range(1, num_of_elements):
        assert response.data['results'][i-1]['altitude'] >= response.data['results'][i]['altitude']


class ScoreTests(APITestCase):
    def test_get(self):
        registered_client = create_registeredclient()
        create_score(registered_client)
        create_score(registered_client)
        response = self.client.get('/scores/registered_clients/' + registered_client.uuid + '/?order_by=score',
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
        self.equal = self.assertEqual(len(response.data['results']), REST_FRAMEWORK['PAGE_SIZE'])

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
        start = timezone.now()
        clients = [create_registeredclient() for i in range(0, 1000)]
        after_clients = timezone.now()

        print("Added clients in " + str(after_clients-start) + "s")

        for i in range(0, 10000):
            client = clients[randint(0, len(clients)-1)]
            create_score(client)

        after_scores = timezone.now()
        print("Added scores in " + str(after_scores-after_clients) + "s")

        response = self.client.get('/scores/registered_clients/' + client.uuid + '/?order_by=altitude',
                                   format='json')

        assert_ordered_by_descending_altitude(response, len(response.data['results']))

        after_response = timezone.now()
        print("Got response in " + str(after_response-after_scores) + "s, for single client")

        response = self.client.get('/scores/?order_by=altitude',
                                   format='json')

        after_response_multi = timezone.now()
        print("Got response in " + str(after_response_multi-after_response) + "s, for all clients")

        assert_ordered_by_descending_altitude(response, REST_FRAMEWORK['PAGE_SIZE'])

    def test_invalid_client_uuid(self):
        registered_client = create_registeredclient()
        create_score(registered_client)
        create_score(registered_client)
        response = self.client.get('/scores/registered_clients/this-is-invalid-uuid/?order_by=score',
                                   format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaginationTests(TestCase):

    def test_pagination_order_by_score(self):
        pagination = ScorePagination()
        registered_client = create_registeredclient()
        score1 = create_score(registered_client)
        score1.score = 1
        score1.save()

        for i in range(REST_FRAMEWORK['PAGE_SIZE']):
            score2 = create_score(create_registeredclient())
            score2.score = 2
            score2.save()

        score3 = create_score(create_registeredclient())
        score3.score = 1
        score3.played_on = score1.played_on - timedelta(days=1)
        score3.save()

        queryset = Score.objects.all().order_by('-score', 'played_on')

        for q in queryset:
            print q.id

        request = Mock()
        request.query_params = {
            'bestof': registered_client.uuid,
            'order_by': 'score'
        }

        page = pagination.paginate_queryset(queryset=queryset, request=request)
        self.assertEquals(pagination.page_number, 2)
        self.assertEquals(page[len(page)-1].id, score1.id)

    def test_pagination_order_by_play_time(self):
        pagination = ScorePagination()
        registered_client = create_registeredclient()
        score1 = create_score(registered_client)
        score1.altitude = 2000
        score1.play_time = 20000
        score1.save()

        for i in range(REST_FRAMEWORK['PAGE_SIZE']):
            score2 = create_score(create_registeredclient())
            score2.altitude = 2000
            score2.play_time = 10000
            score2.save()

        score3 = create_score(create_registeredclient())
        score3.altitude = 5
        score3.play_time = 200
        score3.save()

        queryset = Score.objects.all().order_by('-altitude', 'play_time', 'played_on')

        for q in queryset:
            print q.id

        request = Mock()
        request.query_params = {
            'bestof': registered_client.uuid,
            'order_by': 'altitude'
        }

        page = pagination.paginate_queryset(queryset=queryset, request=request)
        self.assertEquals(pagination.page_number, 2)
        self.assertEquals(page[0].id, score1.id)

    def test_returns_last_page(self):
        pagination = ScorePagination()
        number_of_pages = 2

        for i in range(REST_FRAMEWORK['PAGE_SIZE']*number_of_pages):
            create_score(create_registeredclient())

        queryset = Score.objects.all().order_by('-altitude', 'play_time', 'played_on')

        request = Mock()
        request.query_params = {
            'page': 'last'
        }

        pagination.paginate_queryset(queryset=queryset, request=request)
        self.assertEquals(pagination.page_number, number_of_pages)

    def test_raises_error_on_invalid_page(self):
        pagination = ScorePagination()
        create_score(create_registeredclient())

        queryset = Score.objects.all().order_by('-altitude', 'play_time', 'played_on')

        request = Mock()
        request.query_params = {
            'page': '999999'
        }

        self.assertRaises(NotFound, pagination.paginate_queryset, queryset, request)
