from django.test import TestCase
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from models import RegisteredClient
import datetime


class AccountTests(APITestCase):
    def test_get(self):
        """
        Ensure we can create a new account object.
        """

        registered_client = RegisteredClient()
        registered_client.country = 'Poland'
        registered_client.ip = '212.33.42.138'
        registered_client.date_joined = datetime.datetime.utcnow()
        registered_client.uuid = 'deeda2d0-8d18-45d7-b720-3198c8acf430'
        registered_client.save()

        url = reverse('registered_client')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RegisteredClient.objects.count(), 1)

    def test_post(self):
        url = reverse('registered_client')
        data = {
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
            "phrase": "gibberish text here"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RegisteredClient.objects.count(), 0)

    def test_post_to_short_phrase(self):
        url = reverse('registered_client')
        data = {
            "phrase": "nice wise"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(RegisteredClient.objects.count(), 0)