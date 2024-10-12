from rest_framework.serializers import ModelSerializer
from tgbot.models import Zacup, Botuser


class BotuserSerializer(ModelSerializer):
    class Meta:
        model = Botuser
        fields = ['id', 'user_surname', 'user_name', 'tg_id', 'tg_nic', 'date_of_registration', 'access_granted']

class ZacupSerializer(ModelSerializer):
    bot_user = BotuserSerializer()
    class Meta:
        model = Zacup
        fields = ['id', 'doc_number', 'status', 'booking_date', 'final_date', 'bot_user']

