import telebot
from bot_token import TOKEN
import requests

w_codes = {
        0 : 'чистое небо',
        1 : 'преимущественно ясно',
        2 : 'переменная облачность',
        3 : 'пасмурно',
        45 : 'туман',
        48 : 'налипающий иней',
        51 : 'легкая морось',
        53 : 'умеренная морось',
        55 : 'плотная морось',
        56 : 'моросящий дождь небольшой интенсивности',
        57 : 'моросящий дождь густой интенсивности',
        61 : 'дождь небольшой интенсивности',
        63 : 'дождь умеренной интенсивности',
        65 : 'дождь сильной интенсивности',
        66 : 'ледяной дождь небольшой интенсивности',
        67 : 'ледяной дождь сильной интенсивности',
        71 : 'снегопад небольшой интенсивности',
        73 : 'снегопад умеренной интенсивности',                                                
        75 : 'снегопад сильной интенсивности',
        77 : 'снежная крупа',
        80 : 'слабый ливняной дождь',
        81 : 'умеренный ливняной дождь',
        82 : 'сильный ливняной дождь',
        85 : 'легкий снежный ливень',
        86 : 'сильный снежный ливень',
        95 : 'слабая или умеренная гроза',
        96 : 'гроза с небольшим градом',
        99 : 'гроза с сильным градом'
    }

bot = telebot.TeleBot(TOKEN)

user_states = {}

def get_weather_now(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=ms&timezone=Europe%2FMoscow&forecast_days=1'
    weather = requests.get(url).json()['current']
    text = ' Текущая погода:\n\n'
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
    text += w_codes.get(weather['weather_code'], 'неизвестно').capitalize() + '\n'
    text += f'Скорость ветра: {weather["wind_speed_10m"]} м/с\n'
    win_dirs = ['Север', 'Северо-Восток', 'Восток', 'Юго-Восток', 'Юг', 'Юго-Запад', 'Запад', 'Северо-Запад']
    win_dir = win_dirs[weather['wind_direction_10m'] % 360 // 45]
    text += f'Направление ветра: {win_dir}\n'
    text += f'Порывы ветра: {weather["wind_gusts_10m"]} м/с\n'
    return text

def get_weather_daily(lat, lon):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Europe%2FMoscow&forecast_days=3'
    data = requests.get(url).json()
    daily = data['daily']
    
    text = ' Прогноз на 3 дня:\n\n'
    
    for i in range(len(daily['time'])):
        text += f"{daily['time'][i]}:\n"
        text += f"Температура: {daily['temperature_2m_min'][i]}°C ... {daily['temperature_2m_max'][i]}°C\n"
        text += f"Осадки: {daily['precipitation_sum'][i]} мм\n"
        text += w_codes.get(daily['weather_code'][i], 'неизвестно').capitalize() + '\n\n'
        text += f'Направление ветра: {daily[win_dir][i]}\n'
        text += f'Порывы ветра: {weather["wind_gusts_10m"]} м/с\n'
    return text

@bot.message_handler(commands=['help'])
def helpa(message):
    bot.send_message(message.chat.id, 
                    'Этот бот показывает погоду там, где вы находитесь.\n\n'
                    'Команды:\n'
                    '/start - Текущая погода\n'
                    '/day - Прогноз на 3 дня\n\n'
                    'Для получения данных поделитесь геолокацией')

@bot.message_handler(commands=['start'])
def get_location(msg):
    user_states[msg.chat.id] = 'current'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=1)
    keyboard.add(telebot.types.KeyboardButton('Поделиться геолокацией', request_location=True))
    bot.send_message(msg.chat.id, 'Поделись геолокацией для получения текущей погоды', reply_markup=keyboard)

@bot.message_handler(commands=['day'])
def get_location_daily(msg):
    user_states[msg.chat.id] = 'daily'
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=1)
    keyboard.add(telebot.types.KeyboardButton('Поделиться геолокацией', request_location=True))
    bot.send_message(msg.chat.id, 'Поделись геолокацией для получения прогноза на 3 дня', reply_markup=keyboard)

@bot.message_handler(content_types=['location'])
def send_weather(msg):
    keyboard = telebot.types.ReplyKeyboardRemove()
    
    state = user_states.get(msg.chat.id, 'current')
    
    if state == 'daily':
        text = get_weather_daily(msg.location.latitude, msg.location.longitude)
    else:
        text = get_weather_now(msg.location.latitude, msg.location.longitude)
    
    bot.send_message(msg.chat.id, text, reply_markup=keyboard)



if __name__ == '__main__':
    bot.infinity_polling()

