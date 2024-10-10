from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('api/zacup', views.ZacupView)
router.register('api/botuser', views.BotuserView)


urlpatterns = [
    path('', views.index, name='home'),
    path('settings/', views.bot_settings, name='settings'),
    path('users/', views.users, name='users')
]


urlpatterns += router.urls



