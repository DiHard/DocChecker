from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from tgbot.forms import BotsettingsForm
from tgbot.models import Zacup, Botuser, Botsettings
from tgbot.serializers import ZacupSerializer, BotuserSerializer


@login_required
def index(request):
    zacup_list = Zacup.objects.all().exclude(id=20).order_by('-booking_date')
    content = {
        'title': 'Академия закупок Алексея Дитриха',
        'zacup_list': zacup_list
    }
    return render(request, 'tgbot/index.html', content)# Create your views here.
@login_required
def users(request):
    users_list = Botuser.objects.all().exclude(id=20)
    content = {
        'title': 'Академия закупок Алексея Дитриха',
        'users_list': users_list
    }
    return render(request, 'tgbot/users.html', content)

@login_required
def bot_settings(request):
    # Редактирование настроек проекта
    settings_set = Botsettings.objects.get(id=1)
    error = ''
    form = BotsettingsForm(instance=settings_set)
    context = {
        'form': form,
        'settings_set': settings_set,
        'error': error
    }
    if request.method == 'POST':
        form = BotsettingsForm(request.POST, instance=settings_set)
        if form.is_valid():
            form.save()
            return redirect('home')
            # return render(request, 'tgbot/settings.html', context)
        else:
            error = 'Произошла ошибка сохранения: форма содержала некоректные данные'
    return render(request, 'tgbot/settings.html', context)


class ZacupView(ModelViewSet):
    queryset = Zacup.objects.all().exclude(id=20).order_by('-booking_date')
    serializer_class = ZacupSerializer
    permission_classes = [permissions.IsAuthenticated]


class BotuserView(ModelViewSet):
    queryset = Botuser.objects.all().exclude(id=20)
    serializer_class = BotuserSerializer
    permission_classes = [permissions.IsAuthenticated]