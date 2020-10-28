import shelve

import datetime as dt

from funcs import single_action, double_action, convert_data, which_icon

def frcst_five(data, date, bttn, unq_id):

    # uses 5 day weather forecast that provides data for every 3 hours -> 24h / 3h x 5d = 40 lists
    # detailed info on openweathermap.org/forecast5

    icons = []
    city_name, answer = '', ''
    tmp, press, hum, deg, speed, switch = 0, 0, 0, 0, 0, 0

    with shelve.open('storage', writeback=True) as users:

        if users[unq_id]['lang'] == 'ru':
            if bttn == 'night_bttn':
                time = f'Ночью {date}'
            elif bttn == 'morn_bttn':
                time = f'Утром {date}'
            elif bttn == 'day_bttn':
                time = f'Днём {date}'
            elif bttn == 'even_bttn':
                time = f'Вечером {date}'
        elif users[unq_id]['lang'] == 'en':
            if bttn == 'night_bttn':
                time = f'{date} at night'
            elif bttn == 'morn_bttn':
                time = f'{date} in the morning'
            elif bttn == 'day_bttn':
                time = f'{date} during the day'
            elif bttn == 'even_bttn':
                time = f'{date} in the evening'

        if 'q' in users[unq_id].keys():
            city_name = users[unq_id]['q'].title()
        elif 'lat' in users[unq_id].keys() and 'lon' in users[unq_id].keys():
            lat_nmbr = float(users[unq_id]['lat'])
            lon_nmbr = float(users[unq_id]['lon'])

            if users[unq_id]['lang'] == 'ru':
                if lat_nmbr >= 0:
                    lat_name = 'с. ш.'
                else:
                    lat_name = 'ю. ш.'
                if lon_nmbr >= 0:
                    lon_name = 'в. д.'
                else:
                    lon_name = 'з. д.'
            elif users[unq_id]['lang'] == 'en':
                if lat_nmbr >= 0:
                    lat_name = 'N'
                else:
                    lat_name = 'S'
                if lon_nmbr >= 0:
                    lon_name = 'E'
                else:
                    lon_name = 'W'

            if 'name' in data['city'].keys():
                city_name = data['city']['name'].title()

        for i in range(0, 40):

            # 2020-12-31 -> 31.12.2020
            if dt.datetime.strptime(data['list'][i]['dt_txt'].split()[0], '%Y-%m-%d').strftime('%d.%m.%Y') == date:
                
                if data['list'][i]['dt_txt'].split()[1] == '00:00:00':

                    if bttn == 'night_bttn':
                        c = i
                    elif bttn == 'morn_bttn':
                        c = i + 2
                    elif bttn == 'day_bttn':
                        c = i + 4
                    elif bttn == 'even_bttn':
                        c = i + 6

                    icons, tmp, press, hum, deg, speed, switch = double_action(data, icons, c, tmp, press, hum, deg, speed, switch)
                    break

                # if it's an even number
                elif data['list'][i]['dt_txt'].split()[1] != '00:00:00' and int(data['list'][i]['dt_txt'].split()[1].split(':')[0]) % 2 == 0:

                    if data['list'][i]['dt_txt'].split()[1] == '06:00:00':
                        if bttn == 'morn_bttn':
                            c = i
                        elif bttn == 'day_bttn':
                            c = i + 2
                        elif bttn == 'even_bttn':
                            c = i + 4
                    elif data['list'][i]['dt_txt'].split()[1] == '12:00:00':
                        if bttn == 'day_bttn':
                            c = i
                        elif bttn == 'even_bttn':
                            c = i + 2
                    elif data['list'][i]['dt_txt'].split()[1] == '18:00:00':
                        if bttn == 'even_bttn':
                            c = i

                    icons, tmp, press, hum, deg, speed, switch = double_action(data, icons, c, tmp, press, hum, deg, speed, switch)
                    break             
            
                # if it's an odd number
                elif data['list'][i]['dt_txt'].split()[1] != '00:00:00' and int(data['list'][i]['dt_txt'].split()[1].split(':')[0]) % 2 != 0:

                    if data['list'][i]['dt_txt'].split()[1] == '03:00:00':
                        if bttn == 'night_bttn':
                            c = i
                            icons, tmp, press, hum, deg, speed = single_action(data, icons, c, tmp, press, hum, deg, speed)
                            break
                        elif bttn == 'morn_bttn':
                            c = i + 1
                        elif bttn == 'day_bttn':
                            c = i + 3
                        elif bttn == 'even_bttn':
                            c = i + 5
                    elif data['list'][i]['dt_txt'].split()[1] == '09:00:00':
                        if bttn == 'morn_bttn':
                            c = i
                            icons, tmp, press, hum, deg, speed = single_action(data, icons, i, tmp, press, hum, deg, speed)
                            break
                        elif bttn == 'day_bttn':
                            c = i + 1
                        elif bttn == 'even_bttn':
                            c = i + 3
                    elif data['list'][i]['dt_txt'].split()[1] == '15:00:00':
                        if bttn == 'day_bttn':
                            c = i
                            icons, tmp, press, hum, deg, speed = single_action(data, icons, i, tmp, press, hum, deg, speed)
                            break
                        elif bttn == 'even_bttn':
                            c = i + 1
                    elif data['list'][i]['dt_txt'].split()[1] == '21:00:00':
                        if bttn == 'even_bttn':
                            c = i
                            icons, tmp, press, hum, deg, speed = single_action(data, icons, i, tmp, press, hum, deg, speed)
                            break

                    icons, tmp, press, hum, deg, speed, switch = double_action(data, icons, c, tmp, press, hum, deg, speed, switch)
                    break

    tmp, press, mm, deg, speed = convert_data(tmp, press, deg, speed, unq_id)

    with shelve.open('storage', writeback=True) as users:

        tmp_unit = users[unq_id]['tmp_unit']

        spd_unit = users[unq_id]['spd_unit']

        if c == 0:
            if users[unq_id]['lang'] == 'ru':
                verb = 'составляет'
            elif users[unq_id]['lang'] == 'en':
                verb = 'is'
        else:
            if users[unq_id]['lang'] == 'ru':
                verb = 'будет составлять'
            elif users[unq_id]['lang'] == 'en':
                verb = 'will be'

        if len(icons) > 1:
            fllt = which_icon(icons[0], icons[1])
        else:
            fllt = icons[0]

        if city_name:
            if users[unq_id]['lang'] == 'ru':
                answer = f'{time} температура в населённом пункте {city_name} {verb} {tmp}{tmp_unit}. {fllt} \
Давление: {press} {mm} Влажность: {hum}%. Ветер {deg}, скорость ветра - {speed} {spd_unit}.'
            elif users[unq_id]['lang'] == 'en':
                answer = f'{time} the temperature in {city_name} {verb} {tmp}{tmp_unit}. {fllt} \
Pressure: {press} {mm}. Humidity: {hum}%. {deg} wind around {speed} {spd_unit}.'
        else:
            if users[unq_id]['lang'] == 'ru':
                answer = f'{time} температура в точке с координатами {lat_nmbr}° {lat_name} и {lon_nmbr}° {lon_name} {verb} {tmp}{tmp_unit}. {fllt} \
Давление: {press} {mm} Влажность: {hum}%. Ветер {deg}, скорость ветра - {speed} {spd_unit}.'
            elif users[unq_id]['lang'] == 'en':
                answer = f'{time} the temperature in location with a latitude of {lat_nmbr}° {lat_name} and a longitude of {lon_nmbr}° {lon_name} {verb} {tmp}{tmp_unit}. {fllt} \
Pressure: {press} {mm}. Humidity: {hum}%. {deg} wind around {speed} {spd_unit}.'

    return answer