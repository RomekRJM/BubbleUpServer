from __future__ import unicode_literals

from django.db.models import Model, CharField, DateTimeField, IntegerField, ForeignKey


class RegisteredClient(Model):
    uuid = CharField(max_length=36)
    date_joined = DateTimeField()


class Score(Model):
    registered_client = ForeignKey(RegisteredClient)
    user_name = CharField(max_length=64)
    played_on = DateTimeField()
    recieved_on = DateTimeField()
    play_time = IntegerField()
    altitude = IntegerField()
    score = IntegerField()
    ip = CharField(max_length=50)
