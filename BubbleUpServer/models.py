from __future__ import unicode_literals

from django.db.models import Model, CharField, DateTimeField, IntegerField, ForeignKey


class RegisteredClient(Model):
    uuid = CharField(max_length=36)
    user_name = CharField(max_length=64, unique=True, null=True)
    date_joined = DateTimeField()
    country = CharField(max_length=256, blank=True, null=True)
    state = CharField(max_length=256, blank=True, null=True)
    city = CharField(max_length=256, blank=True, null=True)
    ip = CharField(max_length=40)
    phrase = CharField(max_length=128, blank=True, default='')


class Score(Model):
    registered_client = ForeignKey(RegisteredClient)
    played_on = DateTimeField()
    recieved_on = DateTimeField()
    play_time = IntegerField()
    altitude = IntegerField()
    score = IntegerField()

