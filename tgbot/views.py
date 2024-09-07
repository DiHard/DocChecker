from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tgbot.models import Zacup, Botuser


# Create your views here.
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
