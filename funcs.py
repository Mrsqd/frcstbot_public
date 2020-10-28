import telebot
import shelve
import requests

from consts import api_wthr, api_frcst, params, clds

def failure(unq_id):
    fail = telebot.types.ReplyKeyboardMarkup(True, False)
    with shelve.open('storage', writeback=True) as users:
        if users[unq_id]['lang'] == 'ru':
            geo_bttn = telebot.types.KeyboardButton(text='По моему местоположению', request_location=True)
            fail.row(geo_bttn)
            fail.row('По названию')
            fail.row('По координатам')
        elif users[unq_id]['lang'] == 'en':
            geo_bttn = telebot.types.KeyboardButton(text='By my current location', request_location=True)
            fail.row(geo_bttn)
            fail.row('By city name')
            fail.row('By geographic coordinates')
        return fail

def unknown(unq_id):
    with shelve.open('storage', writeback=True) as users:
        if users[unq_id]['lang'] == 'ru':
            answer = 'На основании полученных данных заданное Вами место установить не удалось. Давайте вернёмся к выбору места:'
        elif users[unq_id]['lang'] == 'en':
            answer = 'According to the given data the place of your interest couldn\'t be determined. Let\'s return to the place selection:'
        return answer

def del_usr_par(unq_id):
    with shelve.open('storage', writeback=True) as users:
        # if new city name was given, deletes old city name from shelve storage
        if 'q' in users[unq_id].keys():
            del users[unq_id]['q']
        # the same with latitude and longitude
        if 'lat' in users[unq_id].keys():
            del users[unq_id]['lat']
        if 'lon' in users[unq_id].keys():
            del users[unq_id]['lon']

# clears old parameters before the new request
def del_req_par():
    if 'q' in params.keys():
        del params['q']
    if 'lat' in params.keys():
        del params['lat']
    if 'lon' in params.keys():
        del params['lon']

def get_data(unq_id, day):
    del_req_par()    
    with shelve.open('storage', writeback=True) as users:
        params['lang'] = users[unq_id]['lang']
        if 'q' in users[unq_id].keys():
            params['q'] = users[unq_id]['q']
        elif 'lat' in users[unq_id].keys() and 'lon' in users[unq_id].keys():
            params['lat'] = users[unq_id]['lat']
            params['lon'] = users[unq_id]['lon']
    res = requests.get(api_wthr if day == 'now' else api_frcst, params=params)
    data = res.json()
    return data

def convert_data(tmp, press, deg, speed, unq_id):
    
    with shelve.open('storage', writeback=True) as users:

        # OWM provides temperature in Kelvin by default
        if users[unq_id]['tmp_unit'] == 'K':
            tmp = round(tmp, 1)
        elif users[unq_id]['tmp_unit'] == '°C':
            tmp = round(tmp - 273.15, 1)
        elif users[unq_id]['tmp_unit'] == '°F':
            tmp = round((tmp - 273.15) * 1.8 + 32, 1)

        # OWM provides pressure in hPa by default -> conversion to mmHg
        press = round(press * 0.75006375541921)

        if users[unq_id]['lang'] == 'ru':
            mm = 'мм рт. ст.'
        elif users[unq_id]['lang'] == 'en':
            mm = 'mmHg'

        if users[unq_id]['lang'] == 'ru':
            if deg == 0 or deg == 360:
                deg = 'северный'
            elif 0 < deg < 90:
                deg = 'северо-восточный'
            elif deg == 90:
                deg = 'восточный'
            elif 90 < deg < 180:
                deg = 'юго-восточный'
            elif deg == 180:
                deg = 'южный'
            elif 180 < deg < 270:
                deg = 'юго-западный'
            elif deg == 270:
                deg = 'западный'
            elif 270 < deg < 360:
                deg = 'северо-западный'
        elif users[unq_id]['lang'] == 'en':
            if deg == 0 or deg == 360:
                deg = 'North'
            elif 0 < deg < 90:
                deg = 'Northeast'
            elif deg == 90:
                deg = 'East'
            elif 90 < deg < 180:
                deg = 'Southeast'
            elif deg == 180:
                deg = 'South'
            elif 180 < deg < 270:
                deg = 'Southwest'
            elif deg == 270:
                deg = 'West'
            elif 270 < deg < 360:
                deg = 'Northwest'

        if users[unq_id]['spd_unit'] == 'м/с' or users[unq_id]['spd_unit'] == 'm/s':
            speed = round(speed, 1)
        elif users[unq_id]['spd_unit'] == 'мили/ч' or users[unq_id]['spd_unit'] == 'mph':
            speed = round((speed * 2.236936), 1)

    return tmp, press, mm, deg, speed

def time_of_day(data, unq_id):

    # keyboard for the first day
    day1_kbrd = telebot.types.InlineKeyboardMarkup()

    with shelve.open('storage', writeback=True) as users:

        if users[unq_id]['lang'] == 'ru':
            night = telebot.types.InlineKeyboardButton(text='Ночью', callback_data='night_bttn')
            morn = telebot.types.InlineKeyboardButton(text='Утром', callback_data='morn_bttn')
            day = telebot.types.InlineKeyboardButton(text='Днём', callback_data='day_bttn')
            even = telebot.types.InlineKeyboardButton(text='Вечером', callback_data='even_bttn')
        elif users[unq_id]['lang'] == 'en':
            night = telebot.types.InlineKeyboardButton(text='Night', callback_data='night_bttn')
            morn = telebot.types.InlineKeyboardButton(text='Morning', callback_data='morn_bttn')
            day = telebot.types.InlineKeyboardButton(text='Day', callback_data='day_bttn')
            even = telebot.types.InlineKeyboardButton(text='Evening', callback_data='even_bttn')

    # adds from 1 to 4 buttons according to the current time
    if 0 <= int(data['list'][0]['dt_txt'].split()[1].split(':')[0]) < 6:
        day1_kbrd.row(night, morn, day, even)
    elif 6 <= int(data['list'][0]['dt_txt'].split()[1].split(':')[0]) < 12:
        day1_kbrd.row(morn, day, even)
    elif 12 <= int(data['list'][0]['dt_txt'].split()[1].split(':')[0]) < 18:
        day1_kbrd.row(day, even)
    elif 18 <= int(data['list'][0]['dt_txt'].split()[1].split(':')[0]) < 24:
        day1_kbrd.row(even)

    #keyboard for the remaining 4 days
    days_kbrd = telebot.types.InlineKeyboardMarkup()
    days_kbrd.row(night, morn, day, even)

    return day1_kbrd, days_kbrd

def single_action(data, icons, i, tmp, press, hum, deg, speed):
    tmp = data['list'][i]['main']['temp']
    icons.append(clds[data['list'][i]['weather'][0]['id']][1])
    press = data['list'][i]['main']['pressure']
    hum = data['list'][i]['main']['humidity']
    deg = data['list'][i]['wind']['deg']
    speed = data['list'][i]['wind']['speed']
    return icons, tmp, press, hum, deg, speed

def double_action(data, icons, c, tmp, press, hum, deg, speed, switch):
    for i in range(c, c + 2):
        tmp += data['list'][i]['main']['temp']
        # if c == 0
        if not press:
            # if one of the icons shows rain and the other shows lightning, replaces them with the icon that combines both
            if 800 <= data['list'][i]['weather'][0]['id'] <= 803 and 300 <= data['list'][i + 1]['weather'][0]['id'] <= 531 or 800 <= data['list'][i + 1]['weather'][0]['id'] <= 803 and 300 <= data['list'][i]['weather'][0]['id'] <= 531:
                icons.append(u'\U0001F326')
                switch = 1
            # if some icons are similar (e.g. scattered clouds & broken clouds), chooses the icon with the higher value -> broken clouds
            if 800 <= data['list'][i]['weather'][0]['id'] <= 804 and 800 <= data['list'][i + 1]['weather'][0]['id'] <= 804:
                more = max(data['list'][i]['weather'][0]['id'], data['list'][i + 1]['weather'][0]['id'])
                icons.append(clds[more][1])
                switch = 1
        else:
            if not switch:
                icons.append(clds[data['list'][i]['weather'][0]['id']][1])
        press += data['list'][i]['main']['pressure']
        hum += data['list'][i]['main']['humidity']
        deg += data['list'][i]['wind']['deg']
        speed += data['list'][i]['wind']['speed']
    tmp = tmp / 2
    press = press  / 2
    hum = round(hum / 2)
    deg /= 2
    speed /= 2
    return icons, tmp, press, hum, deg, speed, switch

def which_icon(icon1, icon2):
    if icon1 == icon2:
        return icon1
    if (icon1 == u'\U000026C8' and icon2 == u'\U0001F327' or icon2 == u'\U0001F329') or (icon2 == u'\U000026C8' and icon1 == u'\U0001F327' or icon1 == u'\U0001F329'):
        return u'\U000026C8'
    if (icon1 == (u'\U0001F327' + ' + ' + u'\U00002744') and icon2 == u'\U0001F327' or icon2 == u'\U00002744') or (icon2 == (u'\U0001F327' + ' + ' + u'\U00002744') and icon1 == u'\U0001F327' or icon1 == u'\U00002744'):
        return u'\U0001F327' + ' + ' + u'\U00002744'
    if icon1 == u'\U00002600' and icon2 != u'\U0001F300' or icon2 != u'\U0001F32A' or icon2 != u'\U0001F32B':
        return icon2
    elif icon2 == u'\U00002600' and icon1 != u'\U0001F300' or icon1 != u'\U0001F32A' or icon1 != u'\U0001F32B':
        return icon1
    if icon1 == u'\U00002601' and icon2 != u'\U00002744' or icon2 != u'\U0001F300' or icon2 != u'\U0001F32A' or icon2 != u'\U0001F32B':
        return icon2
    elif icon2 == u'\U00002601' and icon1 != u'\U00002744' or icon1 != u'\U0001F300' or icon1 != u'\U0001F32A' or icon1 != u'\U0001F32B':
        return icon1
    if icon1 == u'\U0001F327' and icon2 == u'\U0001F329' or icon2 == u'\U0001F327' and icon1 == u'\U0001F329':
        return u'\U000026C8'
    return icon1 + ' + ' + icon2