#!usr/bin/python3

import telebot
import requests
import datetime as dt
import re

# for users' data
import shelve

# for Heroku server
import logging
from os import environ
from flask import Flask, request

# for polling
import time

# constant variables
from consts import bot, codes, days, messages

# supporting functions
from funcs import failure, unknown, del_usr_par, del_req_par, get_data, time_of_day

# weather now, tomorrow's forecast, 5 day weather forecast
from current import wthr_now
from tomorrow import frcst_tom
from five import frcst_five



# start menu
@bot.message_handler(commands=['start', 'help'])
@bot.message_handler(func=lambda msg: msg.text == 'Сбросить мои данные' or msg.text == 'Reset my data' or msg.text == 'Сбросить мои данные / Reset my data' and msg.content_type == 'text')
def start_kbrd(msg):    
    # values by default
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        if msg.from_user.id not in users.keys():
            users[msg.from_user.id] = {}
            if msg.from_user.language_code in codes:
                users[msg.from_user.id]['lang'] = 'ru'
            else:
                users[msg.from_user.id]['lang'] = 'en'
            users[msg.from_user.id]['tmp_unit'] = '°C'
            users[msg.from_user.id]['spd_unit'] = 'м/с'

        start = telebot.types.ReplyKeyboardMarkup(True, False)

        if users[msg.from_user.id]['lang'] == 'ru':
            geo_bttn = telebot.types.KeyboardButton(text='По моему местоположению', request_location=True)
            start.row(geo_bttn)
            start.row('По названию')
            start.row('По координатам')
            if msg.text == '/help':
                bot.send_message(msg.chat.id, text='/start - начало работы с ботом\n\n\
/help - справочная информация\n\n\
/eng - changing language to English\n\n\
/rus - смена языка на русский\n\n\
Данный бот всегда будет рад показать Вам:\n\n\
 - погоду, актуальную на данный момент\n\
 - прогноз погоды на завтра\n\
 - прогноз на следующие 5 дней\n\n\
Выбор места:\n\n\
 - по Вашему местоположению\n\
 - по названию\n\
 - по координатам\n\n\
Координаты (широта от −90° до +90°, долгота от −180° до +180°) должны быть введены в градусах в виде десятичной дроби через пробел. Образец: 57.195 57.88\n\n\
Языки: русский | английский\n\n\
Единицы измерения температуры: °C | °F | °K\n\n\
Единицы измерения скорости: м/с | мили/ч\n\n\
Все данные берутся с онлайн-сервиса OpenWeatherMap.org.\n\n\
По всем вопросам и предложениям обращайтесь по данным контактам: @Mrsqd | gMrsqd@gmail.com.', reply_markup=start)
            else:
                bot.send_message(msg.chat.id, text='Приветствую! Я - бот, который всегда будет рад показать Вам прогноз погоды. Но для начала мне нужно определиться с местом. Как Вы хотите, чтобы я это сделал?', reply_markup=start)
    
        elif users[msg.from_user.id]['lang'] == 'en':
            geo_bttn = telebot.types.KeyboardButton(text='By my current location', request_location=True)
            start.row(geo_bttn)
            start.row('By city name')
            start.row('By geographic coordinates')
            if msg.text == '/help':
                bot.send_message(msg.chat.id, text='/start - launching the bot\n\n\
/help - detailed info\n\n\
/eng - changing language to English\n\n\
/rus - смена языка на русский\n\n\
This bot will always be happy to show you:\n\n\
 - the current weather\n\
 - tomorrow’s forecast\n\
 - 5 day weather forecast\n\n\
Place selection:\n\n\
 - by your current location\n\
 - by city name\n\
 - by geographic coordinates\n\n\
Geographic coordinates (latitude from −90° to +90°, longitude from −180° to +180°) must be entered in space-separated decimal degrees. Example: 37.23 -115.8\n\n\
Languages: English | Russian\n\n\
Temperature units: °C | °F | °K\n\n\
Speed units: m/s | mph\n\n\
All data is supplied by OpenWeatherMap.org.\n\n\
Feel free to contact me here (@Mrsqd) or by email (gMrsqd@gmail.com).', reply_markup=start)
            else:
                bot.send_message(msg.chat.id, text='Hello! I\'m the bot, that will always be happy to show you the weather forecast. But for the start I need to find out the place. How do you want me to do that?', reply_markup=start)

# if 'By my current location' button in the start menu was pressed
@bot.message_handler(content_types=['location'])
def geolocation(msg):
    msg.from_user.id = str(msg.from_user.id)
    if msg.location:
        # shelve can't be nested so del_usr_par comes first
        del_usr_par(msg.from_user.id)
        with shelve.open('storage', writeback=True) as users:
            users[msg.from_user.id]['lat'] = msg.location.latitude
            users[msg.from_user.id]['lon'] = msg.location.longitude
            users[msg.from_user.id]['my_lat'] = msg.location.latitude
            users[msg.from_user.id]['my_lon'] = msg.location.longitude
        main_kbrd(msg)
    else:
        with shelve.open('storage', writeback=True) as users:
            if users[msg.from_user.id]['lang'] == 'ru':
                bot.send_message(msg.chat.id, 'Ваше местоположение установить не удалось.')
            elif users[str(msg.from_user.id)]['lang'] == 'en':
                bot.send_message(msg.chat.id, 'Your location couldn\'t be determined.')

# if the other buttons in the start menu were pressed
@bot.message_handler(func=lambda msg: msg.text == 'По названию' or msg.text == 'By city name' or msg.text == 'По координатам' or msg.text == 'By geographic coordinates' and msg.content_type == 'text')
def want_kbrd(msg):
    want = telebot.types.ReplyKeyboardMarkup(True, False)
    with shelve.open('storage', writeback=True) as users:
        if users[str(msg.from_user.id)]['lang'] == 'ru':
            want.row('Настройки')
            want.row('Вернуться к выбору места')
            if msg.text == 'По названию':
                bot.send_message(msg.chat.id, text='Вводите же, смелее:', reply_markup=want)
            elif msg.text == 'По координатам':
                bot.send_message(msg.chat.id, text='Смелее вводите широту и долготу, разделённые пробелом (например, 57.195 57.88):', reply_markup=want)
        elif users[str(msg.from_user.id)]['lang'] == 'en':
            want.row('Settings')
            want.row('Return to the place selection')
            if msg.text == 'By city name':
                bot.send_message(msg.chat.id, text='Don\'t be shy, enter it:', reply_markup=want)
            elif msg.text == 'By geographic coordinates':
                bot.send_message(msg.chat.id, text='Don\'t be shy, enter space-separared latitude and longitude (e.g. 37.23 -115.8):', reply_markup=want)

# main menu
def main_kbrd(msg):
    main = telebot.types.ReplyKeyboardMarkup(True, False)
    with shelve.open('storage', writeback=True) as users:
        if users[str(msg.from_user.id)]['lang'] == 'ru':
            geo_now = telebot.types.KeyboardButton(text='Погода сейчас')
            geo_tom = telebot.types.KeyboardButton(text='Прогноз на завтра')
            geo_fiv = telebot.types.KeyboardButton(text='Прогноз на 5 дней')
            main.row(geo_now, geo_tom)
            main.row(geo_fiv, 'Настройки')
            main.row('Вернуться к выбору места')
            bot.send_message(msg.chat.id, text='Вы хотите узнать:', reply_markup=main)
        elif users[str(msg.from_user.id)]['lang'] == 'en':
            geo_now = telebot.types.KeyboardButton(text='Current weather')
            geo_tom = telebot.types.KeyboardButton(text='Tomorrow\'s forecast')
            geo_fiv = telebot.types.KeyboardButton(text='5 day weather forecast')
            main.row(geo_now, geo_tom)
            main.row(geo_fiv, 'Settings')
            main.row('Return to the place selection')
            bot.send_message(msg.chat.id, text='You want to find out:', reply_markup=main)

# if 'Current weather' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Погода сейчас' or msg.text == 'Current weather' and msg.content_type == 'text')
def wthr(msg):
    answer = wthr_now(msg)
    if answer.startswith('На основании') or answer.startswith('According to'):
        bot.send_message(msg.chat.id, text=answer, reply_markup=failure(str(msg.from_user.id)))
    else:
        bot.send_message(msg.chat.id, text=answer)

# if 'Tomorrow's forecast' or '5 day weather forecast' buttons were pressed
@bot.message_handler(func=lambda msg: msg.text == 'Прогноз на завтра' or msg.text == 'Tomorrow\'s forecast' or msg.text == 'Прогноз на 5 дней' or msg.text == '5 day weather forecast' and msg.content_type == 'text')
def frcst(msg):
    
    msg.from_user.id = str(msg.from_user.id)

    data = get_data(msg.from_user.id, 'five')

    if msg.text == 'Прогноз на завтра' or msg.text == 'Tomorrow\'s forecast':
        answer = frcst_tom(data, msg.from_user.id)
        if answer.startswith('На основании') or answer.startswith('According to'):
            bot.send_message(msg.chat.id, text=answer, reply_markup=failure(msg.from_user.id))
        else:
            bot.send_message(msg.chat.id, text='\u200c' + answer)

    elif msg.text == 'Прогноз на 5 дней' or msg.text == '5 day weather forecast':

        if data['cod'] == 200 or data['cod'] == '200':

            global days
            global messages

            day1_kbrd, days_kbrd = time_of_day(data, msg.from_user.id)

            # takes the first time value from openweathermap data in order to not depend on time zones
            days[0] = dt.datetime.strptime(data['list'][0]['dt_txt'].split()[0], '%Y-%m-%d').strftime('%d.%m.%Y')

            with shelve.open('storage', writeback=True) as users:
                if users[msg.from_user.id]['lang'] == 'ru':
                    message0 = bot.send_message(msg.chat.id, text='Сегодня', reply_markup=day1_kbrd)
                    messages[message0.chat.id] = [{'message_id': message0.message_id, 'day': 'Сегодня'}, {}, {}, {}, {}]
                elif users[msg.from_user.id]['lang'] == 'en':
                    message0 = bot.send_message(msg.chat.id, text='Today', reply_markup=day1_kbrd)
                    messages[message0.chat.id] = [{'message_id': message0.message_id, 'day': 'Today'}, {}, {}, {}, {}]

            c = 1
            days[1] = (dt.datetime.strptime(days[0], '%d.%m.%Y') + dt.timedelta(days=c)).strftime('%d.%m.%Y')
            message1 = bot.send_message(msg.chat.id, text=days[1], reply_markup=days_kbrd)
            messages[message0.chat.id][1] = {'message_id': message1.message_id, 'day': days[1]}

            c += 1
            days[2] = (dt.datetime.strptime(days[0], '%d.%m.%Y') + dt.timedelta(days=c)).strftime('%d.%m.%Y')
            message2 = bot.send_message(msg.chat.id, text=days[2], reply_markup=days_kbrd)
            messages[message0.chat.id][2] = {'message_id': message2.message_id, 'day': days[2]}

            c += 1
            days[3] = (dt.datetime.strptime(days[0], '%d.%m.%Y') + dt.timedelta(days=c)).strftime('%d.%m.%Y')
            message3 = bot.send_message(msg.chat.id, text=days[3], reply_markup=days_kbrd)
            messages[message0.chat.id][3] = {'message_id': message3.message_id, 'day': days[3]}

            c += 1
            days[4] = (dt.datetime.strptime(days[0], '%d.%m.%Y') + dt.timedelta(days=c)).strftime('%d.%m.%Y')
            message4 = bot.send_message(msg.chat.id, text=days[4], reply_markup=days_kbrd)
            messages[message0.chat.id][4] = {'message_id': message4.message_id, 'day': days[4]}

        elif data['cod'] == 404 or data['cod'] == '404':

            bot.send_message(msg.chat.id, text=unknown(msg.from_user.id), reply_markup=failure(msg.from_user.id))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:

        global messages

        data = get_data(str(call.message.chat.id), 'five')

        # if text == 'Today' or 'Сегодня'
        if len(call.message.text) <= 7:
            date = days[0]
            change = frcst_five(data, date, call.data, str(call.message.chat.id))
        # if text == any date in XX.XX.XXXX format
        elif len(call.message.text) == 10:
            date = call.message.text
            change = frcst_five(data, call.message.text, call.data, str(call.message.chat.id))
        else:
            # regex for any date in XX.XX.XXXX format
            match = re.search(r'(\d\d\.\d\d\.\d{4})', call.message.text)
            change = frcst_five(data, match.group(1), call.data, str(call.message.chat.id))

        day1_kbrd, days_kbrd = time_of_day(data, str(call.message.chat.id))

        for i in range(5):
            # function that replaces the previous answer in 2 ways:
            # 1) if another time of the same day was chosen, replaces it
            # 2) if another day was chosen, gives the new answer and replaces the previous answer with the appropriate date
            if call.message.chat.id in messages.keys() and call.message.message_id == messages[call.message.chat.id][i]['message_id'] and i == 0:
                bot.edit_message_text(text=change, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=day1_kbrd)
            elif call.message.chat.id in messages.keys() and call.message.message_id == messages[call.message.chat.id][i]['message_id'] and i != 0:
                bot.edit_message_text(text=change, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=days_kbrd)
            else:
                try:
                    if i == 0:
                        bot.edit_message_text(text=messages[call.message.chat.id][i]['day'], chat_id=call.message.chat.id, message_id=messages[call.message.chat.id][i]['message_id'], reply_markup=day1_kbrd)
                    elif i != 0:
                        bot.edit_message_text(text=messages[call.message.chat.id][i]['day'], chat_id=call.message.chat.id, message_id=messages[call.message.chat.id][i]['message_id'], reply_markup=days_kbrd)
                except Exception:
                    continue

# settings menu
@bot.message_handler(func=lambda msg: msg.text == 'Настройки' or msg.text == 'Settings' and msg.content_type == 'text')
def sets_kbrd(msg):
    options = telebot.types.ReplyKeyboardMarkup(True, False)
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        if users[msg.from_user.id]['lang'] == 'ru':
            options.row('Поменять язык / Change language')
            options.row('Поменять единицы измерения')
            if 'q' in users[msg.from_user.id].keys() or ('lat' in users[msg.from_user.id].keys() and 'lon' in users[msg.from_user.id].keys()):
                options.row('Вернуться к выбору прогноза', 'Вернуться к выбору места')
            else:
                options.row('Вернуться к выбору места')
            bot.send_message(msg.chat.id, text='Вот что я умею:', reply_markup=options)
        elif users[msg.from_user.id]['lang'] == 'en':
            options.row('Change language / Поменять язык')
            options.row('Change units of measurement')
            # if the city name or its coordinates were given, shows 2 buttons instead of 1
            if 'q' in users[msg.from_user.id].keys() or ('lat' in users[msg.from_user.id].keys() and 'lon' in users[msg.from_user.id].keys()):
                options.row('Return to the forecast selection', 'Return to the place selection')
            else:
                options.row('Return to the place selection')
            bot.send_message(msg.chat.id, text='Here you can:', reply_markup=options)

# if 'Return to the place selection' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Вернуться к выбору места' or msg.text == 'Return to the place selection' and msg.content_type == 'text')
def start_bttn(msg):
    bot.send_message(msg.chat.id, start_kbrd(msg))

# if 'Change language / Поменять язык' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Поменять язык / Change language' or msg.text == 'Change language / Поменять язык' and msg.content_type == 'text')
def lang_kbrd(msg):
    langs = telebot.types.ReplyKeyboardMarkup(True, False)
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        if users[msg.from_user.id]['lang'] == 'ru':
            langs.row('Русский', 'English')
            langs.row('Назад')
        elif users[msg.from_user.id]['lang'] == 'en':
            langs.row('English', 'Русский')
            langs.row('Back')
    if msg.text == 'Русский':
        bot.send_message(msg.chat.id, text='Вы выбрали русский язык!', reply_markup=langs)
    elif msg.text == 'English':
        bot.send_message(msg.chat.id, text='You\'ve chosen English!', reply_markup=langs)
    elif msg.text == 'Поменять язык / Change language':
        bot.send_message(msg.chat.id, text='Пожалуйста, выберите язык: / Please, choose language:', reply_markup=langs)
    elif msg.text == 'Change language / Поменять язык':
        bot.send_message(msg.chat.id, text='Please, choose language: / Пожалуйста, выберите язык:', reply_markup=langs)

@bot.message_handler(func=lambda msg: msg.text == 'Русский' or msg.text == '/rus' or msg.text == 'English' or msg.text == '/eng' and msg.content_type == 'text')
def lang_chc(msg):
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        # if the language was changed, replaces units of speed to another language versions
        if msg.text == 'Русский' or msg.text == '/rus':
            users[msg.from_user.id]['lang'] = 'ru'
            if users[msg.from_user.id]['spd_unit'] == 'm/s':
                users[msg.from_user.id]['spd_unit'] = 'м/с'
            elif users[msg.from_user.id]['spd_unit'] == 'mph':
                users[msg.from_user.id]['spd_unit'] = 'мили/ч'
        elif msg.text == 'English' or msg.text == '/eng':
            users[msg.from_user.id]['lang'] = 'en'
            if users[msg.from_user.id]['spd_unit'] == 'м/с':
                users[msg.from_user.id]['spd_unit'] = 'm/s'
            elif users[msg.from_user.id]['spd_unit'] == 'мили/ч':
                users[msg.from_user.id]['spd_unit'] = 'mph'
    bot.send_message(msg.chat.id, lang_kbrd(msg) if msg.text == 'Русский' or msg.text == 'English' else start_kbrd(msg))

# if 'Change units of measurement' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Поменять единицы измерения' or msg.text == 'Change units of measurement' and msg.content_type == 'text')
def scales_kbrd(msg):
    scales = telebot.types.ReplyKeyboardMarkup(True)
    scales.row('°C', '°F', 'K')
    with shelve.open('storage', writeback=True) as users:
        if users[str(msg.from_user.id)]['lang'] == 'ru':
            scales.row('м/с', 'мили/ч')
            scales.row('Назад')
            bot.send_message(msg.chat.id, text='Пожалуйста, выберите один или несколько интересующих Вас вариантов:', reply_markup=scales)
        elif users[str(msg.from_user.id)]['lang'] == 'en':
            scales.row('m/s', 'mph')
            scales.row('Back')
            bot.send_message(msg.chat.id, text='Select one or several options, please:', reply_markup=scales)

# if 'Return to the forecast selection' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Вернуться к выбору прогноза' or msg.text == 'Return to the forecast selection' and msg.content_type == 'text')
def rtrn_bttn(msg):
    bot.send_message(msg.chat.id, main_kbrd(msg))

# if 'Back' button was pressed
@bot.message_handler(func=lambda msg: msg.text == 'Назад' or msg.text == 'Back' and msg.content_type == 'text')
def back_bttn(msg):    
    bot.send_message(msg.chat.id, sets_kbrd(msg))

# if user wants to change the unit of temperature
@bot.message_handler(func=lambda msg: (msg.text == '°C' or msg.text == '°F' or msg.text == 'K') and msg.content_type == 'text')
def scales_chc(msg):
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        users[msg.from_user.id]['tmp_unit'] = msg.text
        if users[msg.from_user.id]['lang'] == 'ru':
            bot.send_message(msg.chat.id, 'Готово!')
        elif users[msg.from_user.id]['lang'] == 'en':
            bot.send_message(msg.chat.id, 'Ready!')

# if user wants to change the unit of speed
@bot.message_handler(func=lambda msg: (msg.text == 'м/с' or msg.text == 'm/s' or msg.text == 'мили/ч' or msg.text == 'mph') and msg.content_type == 'text')
def speed_chc(msg):
    msg.from_user.id = str(msg.from_user.id)
    with shelve.open('storage', writeback=True) as users:
        users[msg.from_user.id]['spd_unit'] = msg.text
        if users[msg.from_user.id]['lang'] == 'ru':
            bot.send_message(msg.chat.id, 'Выполнено!')
        elif users[msg.from_user.id]['lang'] == 'en':
            bot.send_message(msg.chat.id, 'Completed!')

# processing of city name or geographic coordinates
@bot.message_handler(content_types=['text'])
def main_frcst(msg):
    
    # latitide from −90° to +90° + whitespace + longitude from −180° to +180°
    coor_match = re.match(r"(^[-+]?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+)?))\s+([-+]?(?:180(?:\.0+)?|(?:(?:1[0-7]\d)|(?:[1-9]?\d))(?:\.\d+)?))$", msg.text)
    
    # start of line + ((char|word x 1 + symbol x 1|2) x 0..7 OR number x 0|1|2|3 + symbol x 0|1)) x 0|1 + char|word x 1 + (symbol x 1 + number x 0|1|2|3) x 0|1 + (symbol x 1|2 + word x 1) x 0..8 + end of line
    name_match = re.match(r"^(([a-zA-Zа-яА-Я\u0080-\u024F]+[\., '-]{1,2}){,7}|[0-9]{,3}[\. '-]?)?[a-zA-Zа-яА-Я\u0080-\u024F]+([\. '-][0-9]{,3})?([\., '-]{1,2}[a-zA-Zа-яА-Я\u0080-\u024F]+){,8}$", msg.text)

    msg.from_user.id = str(msg.from_user.id)
    if coor_match:
        # deletes old parameters
        del_usr_par(msg.from_user.id)
        with shelve.open('storage', writeback=True) as users:
            users[msg.from_user.id]['lat'], users[msg.from_user.id]['lon'] = msg.text.split()
        main_kbrd(msg)
    elif name_match:
        del_usr_par(msg.from_user.id)
        with shelve.open('storage', writeback=True) as users:
            users[msg.from_user.id]['q'] = msg.text
        main_kbrd(msg)
    else:
        bot.send_message(msg.chat.id, text=unknown(msg.from_user.id), reply_markup=failure(msg.from_user.id))

# creates a logging instance
logger = logging.getLogger('frcstbot_log')
logger.setLevel(logging.INFO)

# assigns a file-handler to that instance
fh = logging.FileHandler("errors.log")
fh.setLevel(logging.INFO)

# formats all logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter) # This will set the format to the file handler

# adds the handler to the logging instance
logger.addHandler(fh)

if __name__ == '__main__':
    while True:
        try:
            logger.info('Bot running...\n')
            # it's necessary to add this variable to 'dashboard.heroku.com/apps/{APP_NAME}/settings' -> Reveal Config Vars
            if 'HEROKU' in list(environ.keys()):
                server = Flask(__name__)
                @server.route('/bot', methods=['POST'])
                def getMessage():
                    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
                    return '!', 200
                @server.route('/')
                def webhook():
                    bot.remove_webhook()
                    # url='url_of_your_heroku_app/bot'
                    bot.set_webhook(url='https://name_of_your_app.herokuapp.com/bot')
                    return '?', 200
                server.run(host='0.0.0.0', port=environ.get('PORT', 80))
            else:
                # if it launches on developer's computer, it's better to delete webhook
                bot.remove_webhook()
                bot.polling(none_stop=True)
        except Exception:
            logger.exception(Exception)
            logger.info('\n\nRestarting...\n\n\n')
            bot.stop_polling()
            time.sleep(15)