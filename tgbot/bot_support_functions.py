from dateutil import parser

error_text = "Неверный формат даты и времени. Необходимый формат: год-месяц-день часы:минуты.\nПример корректного ввода: 2024-12-25 11:50.\nПопробуйте еще раз."
def translate_months(russian_date_str):
   russian_date_str = russian_date_str.replace('года', '')
   russian_date_str = russian_date_str.replace('год', '')
   russian_date_str = russian_date_str.replace('г.', '')
   russian_date_str = russian_date_str.replace('г', '')
   # Словарь для перевода названий месяцев
   months_translation = {
       "январь": "January",
       "января": "January",
       "февраль": "February",
       "февраля": "February",
       "март": "March",
       "марта": "March",
       "апрель": "April",
       "апреля": "April",
       "май": "May",
       "мая": "May",
       "июнь": "June",
       "июня": "June",
       "июль": "July",
       "июля": "July",
       "август": "August",
       "августа": "August",
       "сентябрь": "September",
       "сентября": "September",
       "октябрь": "October",
       "октября": "October",
       "ноябрь": "November",
       "ноября": "November",
       "декабрь": "December",
       "декабря": "December"
   }
   # Заменяем русские названия месяцев на английские
   for ru_month, en_month in months_translation.items():
       russian_date_str = str(russian_date_str).lower()
       russian_date_str = russian_date_str.replace(ru_month, en_month)
   return russian_date_str


def parse_datetime(input_string):
   try:
       # Используем parser из dateutil для распознавания строки
       data = translate_months(input_string)
       parsed_datetime = parser.parse(data)
       # Приводим к нужному формату
       formatted_datetime = parsed_datetime.strftime("%Y-%m-%d %H:%M")
       return formatted_datetime
   except ValueError:
       return error_text
