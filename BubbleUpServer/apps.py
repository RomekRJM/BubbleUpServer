from __future__ import unicode_literals

from django.apps import AppConfig


class BubbleupserverConfig(AppConfig):
    name = 'BubbleUpServer'

    def ready(self):
        from scheduled import scheduler
        scheduler.start()
