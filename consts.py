import telebot

# current weather
api_wthr = 'http://api.openweathermap.org/data/2.5/weather'

# forecast for tomorrow, 5 days, etc.
api_frcst = 'http://api.openweathermap.org/data/2.5/forecast'

# 'threaded=False' is very important in order to avoid AttibuteError, KeyError or UnpicklingError because of shelve storage deformation
bot = telebot.TeleBot('your_Telegram_API_token', threaded=False)

params = {'appid': 'your_OpenWeather_API_key'}

# codes of countries where Russian language is more preferable that English
codes = {'am', 'az', 'be', 'by', 'kg', 'kz', 'md', 'ru', 'tj', 'tm', 'ua', 'uk', 'uz'}

# translation for weather condition by id, icon/emoji
clds = {200: ['гроза с небольшим дождём', u'\U000026C8'],
        201: ['гроза с дождём', u'\U000026C8'],
        202: ['гроза с сильным дождём', u'\U000026C8'],
        210: ['небольшая гроза', u'\U0001F329'],
        211: ['гроза', u'\U0001F329'],
        212: ['сильная гроза', u'\U0001F329'],
        221: ['переменная гроза', u'\U0001F329'],
        230: ['гроза с лёгкой моросью', u'\U000026C8'],
        231: ['гроза с моросью', u'\U000026C8'],
        232: ['гроза с сильной моросью', u'\U000026C8'],

        300: ['лёгкая морось', u'\U0001F327'],
        301: ['морось', u'\U0001F327'],
        302: ['сильная морось', u'\U0001F327'],
        310: ['легкий моросящий дождь', u'\U0001F327'],
        311: ['моросящий дождь', u'\U0001F327'],
        312: ['сильный моросящий дождь', u'\U0001F327'],
        313: ['дождь', u'\U0001F327'],
        314: ['сильный дождь', u'\U0001F327'],
        321: ['плотная морось', u'\U0001F327'],

        500: ['лёгкий дождь', u'\U0001F327'],
        501: ['умеренный дождь', u'\U0001F327'],
        502: ['сильный дождь', u'\U0001F327'],
        503: ['очень сильный дождь', u'\U0001F327'],
        504: ['сильнейший дождь', u'\U0001F327'],
        511: ['ледяной дождь', u'\U0001F327'],
        520: ['лёгкий ливень', u'\U0001F327'],
        521: ['ливень', u'\U0001F327'],
        522: ['сильный ливень', u'\U0001F327'],
        531: ['переменный ливень', u'\U0001F327'],

        600: ['лёгкий снегопад', u'\U00002744'],
        601: ['снегопад', u'\U00002744'],
        602: ['сильный снегопад', u'\U00002744'],
        611: ['дождь со снегом', u'\U0001F327' + ' + ' + u'\U00002744'],
        612: ['лёгкий дождь со снегом', u'\U0001F327' + ' + ' + u'\U00002744'],
        613: ['дождь со снегом', u'\U0001F327' + ' + ' + u'\U00002744'],
        615: ['лёгкий дождь и снег', u'\U0001F327' + ' + ' + u'\U00002744'],
        616: ['дождь и снег', u'\U0001F327' + ' + ' + u'\U00002744'],
        620: ['лёгкий дождь со снегом', u'\U0001F327' + ' + ' + u'\U00002744'],
        621: ['снегопад', u'\U00002744'],
        622: ['сильный снегопад', u'\U00002744'],

        701: ['туман', u'\U0001F32B'],
        711: ['небольшая дымка', u'\U0001F32B'],
        721: ['лёгкий туман', u'\U0001F32B'],
        731: ['песок, пыль', u'\U0001F32B'],
        741: ['густой туман', u'\U0001F32B'],
        751: ['песок', u'\U0001F32B'],
        761: ['пыль', u'\U0001F32B'],
        762: ['вулканическая пыль', u'\U0001F32B'],
        771: ['шквалы', u'\U0001F300'],
        781: ['торнадо', u'\U0001F32A'],

        800: ['Ясно', u'\U00002600'],
        801: ['небольшая облачность', u'\U0001F324'],
        802: ['переменная облачность', u'\U000026C5'],
        803: ['облачность с прояснениями', u'\U0001F325'],
        804: ['значительная облачность', u'\U00002601']}

days, messages = {}, {}