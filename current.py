import shelve

import datetime as dt

from funcs import get_data, convert_data, unknown

from consts import clds

def wthr_now(msg):

    msg.from_user.id = str(msg.from_user.id)

    # detailed info on openweathermap.org/current
    data = get_data(msg.from_user.id, 'now')

    if data['cod'] == 200 or data['cod'] == '200':

        # conversion to different units of measurement
        tmp, press, mm, deg, speed = convert_data(data['main']['temp'], data['main']['pressure'], data['wind']['deg'], data['wind']['speed'], msg.from_user.id)

        with shelve.open('storage', writeback=True) as users:

            tmp_unit = users[msg.from_user.id]['tmp_unit']

            # each weather condition has its own unique id
            desc = data['weather'][0]['id']

            # gives answer according to weather condition id
            if users[msg.from_user.id]['lang'] == 'ru':
                if 200 <= desc <=  721 or desc == 741 or desc == 781 or 801 <= desc <= 804:
                   fllt = f'Наблюдается {clds[desc][0]}'
                elif desc == 771:
                    fllt = f'Наблюдаются {clds[desc][0]}'
                elif desc == 731:
                    fllt = f'В воздухе присутствуют {clds[desc][0]}'
                elif 751 <= desc <=762:
                    fllt = f'В воздухе присутствует {clds[desc][0]}'
                elif desc == 800:
                    fllt = f'{clds[desc][0]}'
            elif users[msg.from_user.id]['lang'] == 'en':
                fllt = data['weather'][0]['description'].capitalize()

            hum = data['main']['humidity']

            spd_unit = users[msg.from_user.id]['spd_unit']

            # if user's location was given, shows current time
            if 'lat' in users[msg.from_user.id].keys() and 'lon' in users[msg.from_user.id].keys() and 'my_lat' in users[msg.from_user.id].keys() and 'my_lon' in users[msg.from_user.id].keys() and users[msg.from_user.id]['lat'] == users[msg.from_user.id]['my_lat'] and users[msg.from_user.id]['lon'] == users[msg.from_user.id]['my_lon']:
                timestamp = dt.datetime.utcnow().timestamp()
                now = dt.datetime.fromtimestamp(timestamp + data['timezone']).strftime('%d.%m.%Y %H:%M')
                date, time = now.split()
                hours, minutes = time.split(':')
                if users[msg.from_user.id]['lang'] == 'ru':
                    now = f'На {date} {hours}:{minutes}'
                elif users[msg.from_user.id]['lang'] == 'en':
                    now = f'On {date} at {hours}:{minutes}'
            else:
                if users[msg.from_user.id]['lang'] == 'ru':
                    now = 'На данный момент'
                elif users[msg.from_user.id]['lang'] == 'en':
                    now = 'At the moment'

            if 'q' in users[msg.from_user.id].keys():
                city_name = users[msg.from_user.id]['q'].title()
            elif 'lat' in users[msg.from_user.id].keys() and 'lon' in users[msg.from_user.id].keys():
                lat_nmbr = float(users[msg.from_user.id]['lat'])            
                lon_nmbr = float(users[msg.from_user.id]['lon'])

                if users[msg.from_user.id]['lang'] == 'ru':
                    if lat_nmbr >= 0:
                        lat_name = 'с. ш.'
                    else:
                        lat_name = 'ю. ш.'
                    if lon_nmbr >= 0:
                        lon_name = 'в. д.'
                    else:
                        lon_name = 'з. д.'
                elif users[msg.from_user.id]['lang'] == 'en':
                    if lat_nmbr >= 0:
                        lat_name = 'N'
                    else:
                        lat_name = 'S'
                    if lon_nmbr >= 0:
                        lon_name = 'E'
                    else:
                        lon_name = 'W'

                city_name = data['name'].title()
        
            # if city's name was given or was found in json data, shows it / if coordinates were given and they don't define any human settlement, shows them
            if city_name:
                if users[msg.from_user.id]['lang'] == 'ru':
                    answer = f'{now} температура в населённом пункте {city_name} составляет {tmp}{tmp_unit}. {fllt}: {clds[desc][1]}. \
Давление: {press} {mm} Влажность: {hum}%. Ветер {deg}, скорость ветра - {speed} {spd_unit}.'
                elif users[msg.from_user.id]['lang'] == 'en':
                    answer = f'{now} the temperature in {city_name} is {tmp}{tmp_unit}. {fllt}: {clds[desc][1]}. \
Pressure: {press} {mm}. Humidity: {hum}%. {deg} wind around {speed} {spd_unit}.'
            else:
                if users[msg.from_user.id]['lang'] == 'ru':
                    answer = f'{now} температура в точке с координатами {lat_nmbr}° {lat_name} и {lon_nmbr}° {lon_name} составляет {tmp}{tmp_unit}. {fllt}: {clds[desc][1]}. \
Давление: {press} {mm} Влажность: {hum}%. Ветер {deg}, скорость ветра - {speed} {spd_unit}.'
                elif users[msg.from_user.id]['lang'] == 'en':
                    answer = f'{now} the temperature in location with a latitude of {lat_nmbr}° {lat_name} and a longitude of {lon_nmbr}° {lon_name} is {tmp}{tmp_unit}. {fllt}: {clds[desc][1]}. \
Pressure: {press} {mm}. Humidity: {hum}%. {deg} wind around {speed} {spd_unit}.'

    elif data['cod'] == 404 or data['cod'] == '404':

        answer = unknown(msg.from_user.id)
    
    return answer