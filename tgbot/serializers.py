from rest_framework.serializers import ModelSerializer
from tgbot.models import Zacup, Botuser


class ZacupSerializer(ModelSerializer):
    class Meta:
        model = Zacup
        fields = ['id', 'doc_number', 'status', 'booking_date', 'final_date', 'bot_user']


class BotuserSerializer(ModelSerializer):
    class Meta:
        model = Botuser
        fields = ['id', 'user_surname']