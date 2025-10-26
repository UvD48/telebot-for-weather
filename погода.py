import telebot
from bot_token import TOKEN
import requests

w_codes = {
        0 : 'чистое небо',
        1 : 'преимущественно ясно',
        2 : 'переменная облачность',
        3 : 'пасмурно',
        4 : 'туман',
        5 : 'налипающий иней',
        6 : 'легкая морось',
        7 : 'умеренная морось',
        8 : 'плотная морось',
        9 : 'моросящий дождь небольшой интенсивности',
        10 : 'моросящий дождь густой интенсивности',
        11 : 'дождь небольшой интенсивности',
        12 : 'дождь умеренной интенсивности',
        13 : 'дождь сильной интенсивности',
        14 : 'ледяной дождь небольшой интенсивности',
        15 : 'ледяной дождь сильной интенсивности',
        16 : 'снегопад небольшой интенсивности',
        17 : 'снегопад умеренной интенсивности',                                                
        18 : 'снегопад сильной интенсивности',
        19 : 'снежная крупа',
        20 : 'слабый ливняной дождь',
        21 : 'умеренный ливняной дождь',
        22 : 'сильный ливняной дождь',
        23 : 'легкий снежный ливень',
        24 : 'сильный снежный ливень',
        25 : 'слабая или умеренная гроза',
        26 : 'гроза с небольшим градом',
        27 : 'гроза с сильным градом'
    }

bot= telebot.TeleBot(TOKEN) 

bot = telebot.TeleBot(TOKEN)

def get_weather(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow&forecast_days=1'
    weather = requests.get(url).json()['current']
    text = ''
    text += f'Температура: {weather["temperature_2m"]}°C\n'
    text += f'Ощущается как {weather["apparent_temperature"]}°C\n'
    if weather['precipitation'] == 0:
        text += 'Нет осадков\n'
    elif weather['rain'] != 0:
        text += f'Дождь: {weather["rain"]} мм.\n'
    elif weather['showers'] != 0:
        text += f'Ливень: {weather["showers"]} мм.\n'
    elif weather['snowfall'] != 0:
        text += f'Снегопад: {weather["snowfall"]} мм.\n'
    text += w_codes[weather['weather_code']].capitalize() + '\n'
    text += f'Скорость ветра: {weather["wind_speed_10m"]} м/с\n'
    win_dirs = ['Север', 'Северо-Восток', 'Восток', 'Юго-Восток', 'Юг', 'Юго-Запад', 'Запад', 'Северо-Запад']
    win_dir = win_dirs[weather['wind_direction_10m'] % 360 // 45]
    text += f'Направление ветра: {win_dir}\n'
    text += f'Порывы ветра: {weather["wind_gusts_10m"]} м/с\n'
    return text

@bot.message_handler(commands=['help'])
def helpa(message):
    
    bot.send_message(message.chat.id, 'Этот бот показывает погоду там, где вы находитесь, для этого вам надо поделиться геолокацией')

@bot.message_handler(commands=['start'])
def get_location(msg):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=1 )
    keyboard.add(telebot.types.KeyboardButton('Поделиться геолокацией', request_location=True))
    bot.send_message(msg.chat.id, 'Поделись геолокацией', reply_markup=keyboard)

@bot.message_handler(content_types=['location'])
def send_weather(msg):
    keyboard = telebot.types.ReplyKeyboardRemove()
    text = get_weather(msg.location.latitude, msg.location.longitude)
    bot.send_message(msg.chat.id, text, reply_markup=keyboard)




if __name__ == '__main__':
    bot.infinity_polling()
