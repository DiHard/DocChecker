from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tgbot.models import Zacup, Botuser


# Create your views here.
@login_required
def index(request):
    zacup_list = Zacup.objects.all()
    content = {
        'title': 'Главная страница сайта',
        'zacup_list': zacup_list
    }
    return render(request, 'tgbot/index.html', content)# Create your views here.
@login_required
def users(request):
    users_list = Botuser.objects.all()
    content = {
        'title': 'Главная страница сайта',
        'users_list': users_list
    }
    return render(request, 'tgbot/users.html', content)
