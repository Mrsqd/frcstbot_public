import datetime as dt

import shelve

from funcs import convert_data, unknown

from consts import clds

def frcst_tom(data, unq_id):

    answer = ''

    if data['cod'] == 200 or data['cod'] == '200':

        # shows tomorrow's date
        date = (dt.datetime.strptime(data['list'][0]['dt_txt'].split()[0], '%Y-%m-%d') + dt.timedelta(days=1)).strftime('%d.%m.%Y')
        answer += f'{date}\n'

        # uses 5 day weather forecast that provides data for every 3 hours -> takes the first 8 lists in data['list']
        # detailed info on openweathermap.org/forecast5

        for i in range(0, 40):

            # i != 0 in order to show only tomorrow's data if it's 00:00 to 03:00 now
            if data['list'][i]['dt_txt'].split()[1] == '00:00:00' and i != 0:
                
                for i in range(i, i + 8):

                    tmp, press, mm, deg, speed = convert_data(data['list'][i]['main']['temp'], data['list'][i]['main']['pressure'], data['list'][i]['wind']['deg'], data['list'][i]['wind']['speed'], unq_id)

                    with shelve.open('storage', writeback=True) as users:
                        
                        tmp_unit = users[unq_id]['tmp_unit']

                        desc = data['list'][i]['weather'][0]['id']
                        icon = clds[desc][1]

                        hum = data['list'][i]['main']['humidity']

                        deg = data['list'][i]['wind']['deg']

                        if users[unq_id]['lang'] == 'ru':
                            if deg == 0 or deg == 360:
                                deg = 'C'
                            elif 0 < deg < 90:
                                deg = 'С-В'
                            elif deg == 90:
                                deg = 'В'
                            elif 90 < deg < 180:
                                deg = 'Ю-В'
                            elif deg == 180:
                                deg = 'Ю'
                            elif 180 < deg < 270:
                                deg = 'Ю-З'
                            elif deg == 270:
                                deg = 'З'
                            elif 270 < deg < 360:
                                deg = 'С-З'
                        elif users[unq_id]['lang'] == 'en':
                            if deg == 0 or deg == 360:
                                deg = 'N'
                            elif 0 < deg < 90:
                                deg = 'NE'
                            elif deg == 90:
                                deg = 'E'
                            elif 90 < deg < 180:
                                deg = 'SE'
                            elif deg == 180:
                                deg = 'S'
                            elif 180 < deg < 270:
                                deg = 'SW'
                            elif deg == 270:
                                deg = 'W'
                            elif 270 < deg < 360:
                                deg = 'NW'

                        spd_unit = users[unq_id]['spd_unit']

                        # shows every 3 hours: 00:00, 03:00, etc.
                        time = str(data['list'][i]['dt_txt'].split()[1][:-3])

                        if users[unq_id]['lang'] == 'ru':
                            answer += f'\nВремя: {time}. Температура: {tmp}{tmp_unit} {icon} Давление: {press} {mm} Влажность: {hum}%. Ветер {deg}, {speed} {spd_unit}.\n'
                        elif users[unq_id]['lang'] == 'en':
                            answer += f'\nTime: {time}. Temperature: {tmp}{tmp_unit} {icon} Pressure: {press} {mm}. Humidity: {hum}%. {deg} wind, {speed} {spd_unit}.\n'
                break

    elif data['cod'] == 404 or data['cod'] == '404':

        answer = unknown(unq_id)
    
    return answer