from time import sleep
import telebot
from telebot import types
from datetime import datetime, timedelta
import schedule
import threading

# Импорты для работы с базой джанго
import os, sys
import django

from bot_support_functions import error_text, parse_datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DNC.settings")
django.setup()

from tgbot.models import Botuser, Zacup, Botsettings

botsettings = Botsettings.objects.get(id=1)

API_TOKEN = botsettings.bot_token
Admin_tgid = botsettings.admin_tgid

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
   all_users = Botuser.objects.all()
   chat_id = message.chat.id
   its_new_user = True
   for user in all_users:
      if user.tg_id == chat_id:
          if user.access_granted:
              bot.send_message(chat_id, f"Здравствуйте, {user.user_name}.\nДля бронирования просчета введите номер закупки.")
              bot.register_next_step_handler(message, check_user)
          else:
              bot.send_message(chat_id,
                               f"Здравствуйте, {user.user_name}.\nНа текущий момент Ваш доступ к боту не подтвержден.\nОжидайте подтверждения или свяжитесь с администрацией.")
              bot.register_next_step_handler(message, start)
          its_new_user = False
          break
   if its_new_user:
      bot.send_message(chat_id, "Для использования сервиса необходимо получить разрешение администратора. Для составления заявки напишите Вашу фамилию:")
      bot.register_next_step_handler(message, get_surname)

# Регистрация пользователя
def get_surname(message):
   chat_id = message.chat.id
   if message.text == '/start':
       bot.send_message(chat_id, "Команда Start не может являтся фамилией. Введите Вашу фамилию.")
       bot.register_next_step_handler(message, get_surname)
   else:
      surname = message.text
      bot.send_message(chat_id, "Напишите Ваше имя:")
      bot.register_next_step_handler(message, get_name, surname)

def get_name(message, surname):
    chat_id = message.chat.id
    # Создаем встроенную клавиатуру
    markup = types.InlineKeyboardMarkup()
    # Создаем кнопки
    approve_button = types.InlineKeyboardButton("✅Открыть доступ", callback_data='approve')
    unapprove_button = types.InlineKeyboardButton("❌Заблокировать пользователя", callback_data='unapprove')
    # Добавляем кнопки на клавиатуру
    markup.add(approve_button, unapprove_button)
    if message.text == '/start':
        bot.send_message(chat_id, "Команда Start не может являтся именем. Введите Ваше имя.")
        bot.register_next_step_handler(message, get_name, surname)
    else:
       tg_user = Botuser()
       tg_user.user_surname = surname
       tg_user.user_name = message.text
       tg_user.tg_id = message.from_user.id
       tg_user.date_of_registration = datetime.now()
       tg_user.access_granted = False
       if message.from_user.username == None:
           tg_user.tg_nic = "(Ник не указан в профиле)"
       else:
           tg_user.tg_nic = "@" + message.from_user.username

       tg_user.save()
       bot.send_message(chat_id, f"{tg_user.user_name}, заявка успешно составлена, ожидайте подтверждения.")
       bot.register_next_step_handler(message, start)
       bot.send_message(Admin_tgid,
                        f"Пользователь {tg_user.tg_nic} зарегистрировался как {surname} {tg_user.user_name} и подал запрос на доступ к сервису | id={tg_user.id}",
                        reply_markup=markup)

# Конец регистрации пользователя


def check_user(message):
    chat_id = message.chat.id
    try:
        user = Botuser.objects.get(tg_id=chat_id)
        if user.access_granted:
            check_number(message)
        else:
            bot.send_message(chat_id, "Для Вашего профиля ограниен доступ к системе. Обратитесь к администратору сервиса.")
            bot.clear_step_handler_by_chat_id(chat_id)
            clear_bot_buttons(message.id, chat_id)
            bot.register_next_step_handler(message, start)
    except:
        bot.send_message(chat_id, "Ваш провиль не найден в системе. Обратитесь к администратору сервиса.")
        bot.clear_step_handler_by_chat_id(chat_id)
        clear_bot_buttons(message.id, chat_id)


# Проверка номера договора
def check_number(message):
   chat_id = message.chat.id
   doc_number = message.text
   register_number = Zacup.objects.exclude(status="Свободный")
   number_free = True
   # Создаем встроенную клавиатуру
   markup = types.InlineKeyboardMarkup()
   # Создаем кнопки
   zabronirovat_button = types.InlineKeyboardButton("Забронировать заявку", callback_data='zabronirovat')
   # Добавляем кнопки на клавиатуру
   markup.add(zabronirovat_button)
   if message.text == '/start':
       bot.send_message(chat_id, "Бот запущен, введите номер заявки для проверки.")
       bot.register_next_step_handler(message, check_user)
   else:
       for el in register_number:
           if doc_number.upper().replace(" ", "") == el.doc_number:
               number_free = False
               print(el.bot_user.tg_id)
               print(chat_id)
               if el.bot_user.tg_id == chat_id:
                   usermenu = types.InlineKeyboardMarkup()
                   # Создаем кнопки
                   rentable_button = types.InlineKeyboardButton("✅УЧАСТВУЕМ", callback_data='rentable')
                   victory_button = types.InlineKeyboardButton("⭐ПОБЕДА", callback_data='victory')
                   otcaz_button = types.InlineKeyboardButton("❌ОТКАЗ", callback_data='otcaz')
                   dont_win_button = types.InlineKeyboardButton("❌НЕ ВЫИГРАЛ", callback_data='otcaz')
                   change_time_button = types.InlineKeyboardButton("🔄️Поменять время", callback_data='change_time')
                   nothing_button = types.InlineKeyboardButton("Скрыть кнопку", callback_data='nothing')
                   # Добавляем кнопки на клавиатуру
                   if el.status == "Участвуем":
                       usermenu.add(victory_button, change_time_button, dont_win_button, nothing_button)
                       text_message = f"Информация по закупке №{el.doc_number} -->\nЗакупка закреплена за Вами.\nСтатус закупки: {el.status}.\nВремя окончания приема заявок: {(el.final_date).strftime("%d.%m.%Y %H:%M")}\nВы можете перевести закупку в статус 'Победа' или отказатся от просчета"
                       bot.send_message(chat_id, text_message, reply_markup=usermenu)
                   elif el.status == "Победа":
                       text_message = f"Информация по закупке №{el.doc_number} -->\nЗакупка закреплена за Вами.\nСтатус закупки: {el.status}.\nЭто закупка, в которой вы победили!"
                       bot.send_message(chat_id, text_message)
                   else:
                       usermenu.add(rentable_button, otcaz_button, nothing_button)
                       text_message = f"Информация по закупке №{el.doc_number} -->\nЗакупка закреплена за Вами.\nСтатус закупки: {el.status}.\nВы можете перевести закупку в статус 'Участвуем' или отказатся от просчета"
                       bot.send_message(chat_id, text_message, reply_markup=usermenu)
                   bot.register_next_step_handler(message, check_user)
               else:
                   bot.send_message(chat_id, f"Информация по закупке №{el.doc_number} -->\n❌ Эта закупка уже занята другим сотрудником.\nСтатус закупки: {el.status}.\nДата бронирования: {str(el.booking_date)[0:16]}\nДля проверки другой закупки введите номер тендера.")
                   bot.register_next_step_handler(message, check_user)
               break
       if number_free:
           bot.reply_to(message, "✅ Закупка свободна для просчета", reply_markup=markup)
           bot.register_next_step_handler(message, check_user)


def set_status_rentable(message, doc_number):
    final_date = parse_datetime(message.text)
    print(final_date)
    if final_date == error_text:
        bot.send_message(message.chat.id, error_text)
        bot.register_next_step_handler(message, set_status_rentable, doc_number)
    else:
        markup = types.InlineKeyboardMarkup()
        ok_time_button = types.InlineKeyboardButton("✅Время верное", callback_data='ok_time')
        change_time_button = types.InlineKeyboardButton("🔄️Поменять время", callback_data='change_time')
        markup.add(ok_time_button, change_time_button)
        zacup = Zacup.objects.get(doc_number=doc_number)
        zacup.status = "Участвуем"
        zacup.final_date = datetime.fromisoformat(final_date)
        zacup.save()
        bot.send_message(message.chat.id, f"Для закупки №{doc_number} --> сохранена дата окончания приема заявок: {(zacup.final_date).strftime("%d.%m.%Y %H:%M")} и закупка переведена в статус 'Участвуем'.\nЕсли нужно указать другую дату или время, то нажмите кнопку 'Поменять время'", reply_markup=markup)
        bot.register_next_step_handler(message, check_user)


# Эта часть кода отвечает за действия по нажатию кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
   if call.data == 'rentable':
       # Очищаем регистр следующих шагов
       bot.clear_step_handler_by_chat_id(call.message.chat.id)
       print("--")# Отправляем ID пользователя
       print(call.message.message_id)
       bot.delete_message(call.message.chat.id, call.message.id)
       doc_number = call.message.text
       print(doc_number)
       doc_number = doc_number[doc_number.find('№')+1:doc_number.find('-->')-1]
       print(doc_number)
       bot.send_message(call.message.chat.id, f"Для перевода в статус 'Участвуем' укажите дату и время окончания приема заявок.")
       bot.register_next_step_handler(call.message, set_status_rentable, doc_number)
       # Функция очищения кнопок у старых сообщений
       clear_bot_buttons(call.message.id, call.message.chat.id)
   elif call.data == 'victory':
       print(call)# Отправляем ID пользователя
       bot.delete_message(call.message.chat.id, call.message.id)
       doc_number = call.message.text
       print(doc_number)
       doc_number = doc_number[doc_number.find('№')+1:doc_number.find('-->')-1]
       print(doc_number)
       user = Botuser.objects.get(tg_id=call.message.chat.id)
       # Формируем кнопки
       markup = types.InlineKeyboardMarkup()
       victory_yes_button = types.InlineKeyboardButton("⭐Подтвердить победу", callback_data='victory_yes')
       victory_no_button = types.InlineKeyboardButton("❌Отклонить", callback_data='victory_no')
       markup.add(victory_yes_button, victory_no_button)
       bot.send_message(call.message.chat.id, f"Создан запрос для закупки №{doc_number} на перевод в статус 'Победа'.")
       bot.send_message(Admin_tgid, f"Пользователь {user.user_name} {user.user_surname} - {user.tg_nic}.\nПредлагает перевести закупку №{doc_number} --> в статус 'Победа'.", reply_markup=markup)
   elif call.data == 'otcaz':
       print(call)# Отправляем ID пользователя
       bot.delete_message(call.message.chat.id, call.message.id)
       doc_number = call.message.text
       print(doc_number)
       doc_number = doc_number[doc_number.find('№')+1:doc_number.find('-->')-1]
       print(doc_number)
       zacup = Zacup.objects.get(doc_number=doc_number)
       zacup.status = "Свободный"
       zacup.save()
       bot.send_message(call.message.chat.id, f"Закупка №{doc_number} переведена в статус 'Свободный'")

   elif call.data == 'nothing':
       bot.delete_message(call.message.chat.id, call.message.id)
       clear_bot_buttons(call.message.id, call.message.chat.id)
   elif call.data == 'waiting':
       bot.delete_message(call.message.chat.id, call.message.id)
       doc_number = call.message.text
       doc_number = doc_number[doc_number.find('№')+1:doc_number.find('-->')-1]
       zacup = Zacup.objects.get(doc_number=doc_number)
       zacup.final_date = zacup.final_date + timedelta(hours=72)
       zacup.save()
       bot.send_message(zacup.bot_user.tg_id, f"По закупке №{doc_number} проверка отложена на 72 часа.")
   elif call.data == 'victory_yes':
       doc_number = call.message.text
       doc_number = doc_number[doc_number.find('№')+1:doc_number.find('-->')-1]
       zacup = Zacup.objects.get(doc_number=doc_number)
       zacup.status = "Победа"
       zacup.save()
       congratulations = "Ура! ПОЗДРАВЛЯЮ!!! 🎈🥳🎉🙌🎊!!! Мы ПОБЕДИЛИ!!! ⭐"
       bot.send_message(zacup.bot_user.tg_id, f"Закупка №{zacup.doc_number} переведена в статус 'Победа'")
       sleep(1)
       bot.send_message(zacup.bot_user.tg_id, f"{congratulations}")
       bot.send_message(Admin_tgid, f"Закупка №{zacup.doc_number} переведена в статус 'Победа'\nПользователю отправлено сообщение:\n\n{congratulations}")
   elif call.data == 'victory_no':
       doc_number = call.message.text
       doc_number = doc_number[doc_number.find('№') + 1:doc_number.find('-->') - 1]
       zacup = Zacup.objects.get(doc_number=doc_number)
       bot.send_message(zacup.bot_user.tg_id, f"Для закупки №{zacup.doc_number} статус 'Победа' не подтвержден. Вы можете повтороно направить запрос.")
       bot.send_message(Admin_tgid,f"Для закупки №{zacup.doc_number} перевод в статус 'Победа' ОТМЕНЕН.")
   elif call.data == 'approve':
       bot.delete_message(call.message.chat.id, call.message.id)
       userid = call.message.text
       userid = int(userid[userid.find('=') + 1:999])
       botuser = Botuser.objects.get(id=userid)
       botuser.access_granted = True
       botuser.save()
       bot.send_message(Admin_tgid, f"Пользователю {botuser.tg_nic} открыт доступ к сервису.")
       bot.send_message(botuser.tg_id, f"Вам одобрен доступ. Для начала работы нажмите /start")
   elif call.data == 'unapprove':
       bot.delete_message(call.message.chat.id, call.message.id)
       userid = call.message.text
       userid = int(userid[userid.find('=') + 1:999])
       botuser = Botuser.objects.get(id=userid)
       bot.send_message(Admin_tgid, f"Пользователю {botuser.tg_nic} отказано в доступе к сервису.")
       bot.send_message(botuser.tg_id, f"Вам отказано в доступе к сервису. Для уточнения информации свяжитесь с руководством.")
   elif call.data == 'ok_time':
       bot.delete_message(call.message.chat.id, call.message.id)
       clear_bot_buttons(call.message.id, call.message.chat.id)
   elif call.data == 'change_time':
       bot.delete_message(call.message.chat.id, call.message.id)
       bot.clear_step_handler_by_chat_id(call.message.chat.id)
       doc_number = call.message.text
       doc_number = doc_number[doc_number.find('№') + 1:doc_number.find('-->') - 1]
       bot.send_message(call.message.chat.id, f"Укажите дату и время окончания приема заявок в формате: год-месяц-день часы:минуты. Например 2024-12-25 11:50")
       bot.register_next_step_handler(call.message, set_status_rentable, doc_number)
       clear_bot_buttons(call.message.id, call.message.chat.id)
   elif call.data == 'zabronirovat':
       try:
           doc_number = call.json["message"]['reply_to_message']['text'].upper().replace(" ", "")
           print(doc_number)
           zacup = Zacup.objects.get(doc_number=doc_number)
           zacup.status = "На просчете"
           zacup.booking_date = datetime.now()
           zacup.bot_user = Botuser.objects.get(tg_id=call.from_user.id)
           zacup.save()
           # bot.send_message(call.message.chat.id, f"Закупка №{doc_number} переведена в статус 'Свободный'")
       except:
           print(call.message.text)
           print(call)
           print(call.from_user.username)
           zacup = Zacup()
           zacup.doc_number = call.json["message"]['reply_to_message']['text'].upper().replace(" ", "")
           zacup.booking_date = datetime.now()
           zacup.final_date = None
           zacup.bot_user = Botuser.objects.get(tg_id=call.from_user.id)
           zacup.status = "На просчете"
           zacup.save()
           # Отправляем ID чата
       bot.send_message(call.message.chat.id, f"Вы забронировали закупку: {zacup.doc_number}\nЗакупка забронирована за Вами на 48 часов для просчета.")
       clear_bot_buttons(call.message.id, call.message.chat.id)
# Конец кода отвечающего за действия по нажатию кнопок



# Функция очищения чата от сообщений с кнопками
def clear_bot_buttons(message_id, chat_id):
    for i in range(message_id, message_id - 20, -1):  # используем шаг -1, чтобы перебирать в обратном порядке
        try:
            bot.edit_message_reply_markup(chat_id, i, ' ', reply_markup=None)
        except:
            print('Нельзя редактировать')

# Задачи по расписанию
def send_daily_message():
   time_off_zacup = Zacup.objects.filter(status="На просчете")
   time_now = datetime.now()
   for el in time_off_zacup:
       old_time = str(el.booking_date)
       old_time = old_time[0:old_time.find('+')]
       delta_time = time_now - datetime.fromisoformat(old_time)
       if 151200 < delta_time.total_seconds() < 215999: # 42 часа
           print(f'Обнаружено превышение {el.doc_number} - {delta_time.total_seconds()}')
           # Отправляем предупреждение:
           # Создаем встроенную клавиатуру
           markup = types.InlineKeyboardMarkup()
           rentable_button = types.InlineKeyboardButton("✅Участвуем", callback_data='rentable')
           otcaz_button = types.InlineKeyboardButton("❌ Отказаться", callback_data='otcaz')
           markup.add(rentable_button, otcaz_button)
           bot.send_message(el.bot_user.tg_id,
                            f"Информация по закупке №{el.doc_number} -->\n\n⌛Отведенное время на просчет заканчивается, осталось менее 6 часов.\nПодтвердите участие в закупке для закрепления за Вами, иначе закупка станет свободна для бронирования дургими участниками.", reply_markup=markup)
       elif delta_time.total_seconds() > 216000:  # 60 часов
           el.status = "Свободный"
           el.save()
           bot.send_message(el.bot_user.tg_id,
                            f"Информация по закупке №{el.doc_number} -->\nЗакупка переведена в статус 'Свободный', поскольку закончилось время на просчет.\nВы можете заново забронировать закупку за собой, если это необходимо.")



def check_victory():
    zacups = Zacup.objects.filter(status='Участвуем')
    time_now = datetime.now()
    for el in zacups:
        old_time = str(el.final_date)
        old_time = old_time[0:old_time.find('+')]
        delta_time = time_now - datetime.fromisoformat(old_time)
        if delta_time.total_seconds() < 259200:
            markup = types.InlineKeyboardMarkup()
            rentable_button = types.InlineKeyboardButton("⭐ДА", callback_data='victory')
            otcaz_button = types.InlineKeyboardButton("❌НЕТ", callback_data='otcaz')
            waiting_button = types.InlineKeyboardButton("⏳Подведение итогов", callback_data='waiting')
            markup.add(rentable_button, otcaz_button, waiting_button)
            bot.send_message(el.bot_user.tg_id,
                             f"Информация по закупке №{el.doc_number} -->\n\n⌛После окончания времени подачи заявки прошло более 72 часов. Мы победили?",
                             reply_markup=markup)


def close_access():
    users = Botuser.objects.filter(access_granted=True).exclude(id=20)
    data = datetime.now() - timedelta(days=31)
    for el in users:
        zacups = Zacup.objects.filter(bot_user=el).filter(booking_date__gte=data)
        if not any(zacups):
            message = (f'У пользователя {el.user_surname} {el.user_name} нет новых закупок более 30 дней.'
                  f' Пользователю закрыт доступ к боту.')
            el.access_granted = False
            el.save()
            bot.send_message(Admin_tgid, message)
            bot.send_message(373322649, message)

def schedule_messages():
   time = botsettings.check_time
   schedule.every().day.at(time).do(send_daily_message)
   schedule.every().day.at(time).do(check_victory)
   schedule.every().day.at(time).do(close_access)
   while True:
       schedule.run_pending()
       sleep(1)  # Задержка в 1 секунду для снижения нагрузки на CPU


def reolad_bot():
   all_users = Botuser.objects.all()
   for el in all_users:
       # print(el.tg_id, el.access_granted)
       if el.access_granted:
           bot.register_next_step_handler_by_chat_id(el.tg_id, check_user)
       else:
           bot.register_next_step_handler_by_chat_id(el.tg_id, start)


# Создаем и запускаем поток для планирования
threading.Thread(target=schedule_messages, daemon=True).start()

reolad_bot()

bot.send_message(373322649, "Бот был перезапущен.")

# Для работы бота обычно используется polling, но бот тогда часто перезапускается, тк им не пользуются долго,
# infinity_polling решает эту проблему
# bot.polling()
bot.infinity_polling(timeout=10, long_polling_timeout = 5)