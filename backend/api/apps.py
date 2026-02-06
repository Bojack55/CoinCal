from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        # Signals removed to rely on UserProfile.save() logic for robustness
        pass
