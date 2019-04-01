from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'

    # runs signals.py
    def ready(self):
        import users.signals