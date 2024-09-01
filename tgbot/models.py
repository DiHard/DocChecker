from django.db import models

class Botuser(models.Model):
    user_surname = models.CharField('Фамилия', max_length=250)
    user_name = models.CharField('Имя', max_length=250)
    tg_id = models.IntegerField('Telegram ID')
    tg_nic = models.CharField('Ник в телеграм', max_length=250)
    date_of_registration = models.DateField('Дата регистрации')
    access_granted = models.BooleanField('Доступ разрешен')

    def __str__(self):
        return self.user_surname

    class Meta:
        verbose_name = "Зарегистрированный пользователь"
        verbose_name_plural = "Зарегистрированные пользователи"

class Zacup(models.Model):
    doc_number = models.CharField('Номер договора', max_length=250)
    status = models.CharField('Статус', max_length=250)
    booking_date = models.DateTimeField('Дата и время бронирования')
    final_date = models.DateTimeField('Дата и время окончания подачи заявок', null=True, blank=True)
    bot_user = models.ForeignKey(Botuser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.doc_number)

    class Meta:
        verbose_name = "Забронированный договор"
        verbose_name_plural = "Забронированные договоры"

class Botsettings(models.Model):
    admin_tgid = models.IntegerField('Telegram ID администратора')
    check_time = models.CharField('Время проверки статусов', max_length=250)
    bot_token = models.CharField('Токен бота Telegram', max_length=250)


    def __str__(self):
        return "Настройки сервиса"

    class Meta:
        verbose_name = "Настройки"
        verbose_name_plural = "Настройки"