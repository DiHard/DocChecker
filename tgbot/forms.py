from tgbot.models import Botsettings
from django.forms import ModelForm, TextInput


class BotsettingsForm(ModelForm):
    class Meta:
        model = Botsettings
        fields = ['admin_tgid', 'check_time', 'bot_token']
        widgets = {
            'admin_tgid': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Только цифры'
            }),
            'bot_token': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Токен'
            }),
            'check_time': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00:00'
            })
        }