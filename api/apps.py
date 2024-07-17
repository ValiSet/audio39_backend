from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Конфигурация приложения API.

    Attributes:
        default_auto_field (str): Тип автоинкрементного поля по умолчанию для модели.
        name (str): Имя приложения.
        verbose_name (str): Читаемое имя приложения.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API Application'