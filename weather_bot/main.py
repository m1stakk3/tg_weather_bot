import json
import telebot
from telebot import types
import time
import emoji
import random
from weather_db import WeatherDB
from geopy import geocoders
import requests as req


bot = telebot.TeleBot('5391125434:AAFlzh892726_nopmhbHFKeDC4STX6SjZF0')
yandex_api_key = '14408fd2-20ad-4c62-8c17-fb3ab5ff4941'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """На старте работы с ботом"""
    if message.text == '/start':
        username = message.from_user.first_name
        emoji_list = ['☔', '☁', '☀', '🌧', '⛅', '🌀', '🌨', '⛈', '🌩', '🌥', '🌦', '❄']
        bot.send_message(message.chat.id, random.choice(emoji_list)+f' Добро пожаловать {username}, '
                                                                                  f'я погодный бот!')
        bot.send_message(message.chat.id, emoji.emojize(':round_pushpin: Введите Ваш город.'))



@bot.message_handler(content_types=['text'])
def get_city(message):
    if message.text.title() in ['Да', 'Нет']:
        global ans
        ans = message.text.title()
    """Переменные, которые неоднократно используются в коде"""
    city = message.text.title()
    user_id = message.from_user.id


    def geo_pos(city):
        """Определяет широту и долготу"""
        geolcator = geocoders.Nominatim(user_agent='bot')
        lat = str(geolcator.geocode(city).latitude)
        lon = str(geolcator.geocode(city).longitude)
        return lat, lon

    def db_actions(user_id, city, lat, lon):
        """Действия по поиску данных в БД, например сравнение введенего от юзера города с уже имеющимся"""
        if WeatherDB().user_exists(user_id) is False:
            WeatherDB().add_user(user_id, city, lat, lon)
            WeatherDB().close()
            return True

        if WeatherDB().current_city(user_id) != city:
            return False

    db_actions(user_id, city, geo_pos(city)[0], geo_pos(city)[1])

    def yandex_weather(lat, lon, key: str):
        url_yandex = f'https://api.weather.yandex.ru/v2/informers/?lat={lat}&lon={lon}&[lang=ru_RU]'
        yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': key}, verify=False)
        conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                          'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                          'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                          'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                          'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                          'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                          'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                          }
        wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                        'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}

        yandex_json = json.loads(yandex_req.text)
        weather = yandex_json['fact']
        temp = weather['temp']
        real_feel = weather['feels_like']
        condition = conditions[weather['condition']]
        ws = weather['wind_speed']
        wd = wind_dir[weather['wind_dir']]
        humidity = weather['humidity']
        pogoda = [temp,real_feel,condition,ws,wd,humidity]
        return pogoda

    w_res = yandex_weather(geo_pos(city)[0], geo_pos(city)[1], yandex_api_key)

    def answer(w_res):
        bot.send_message(message.chat.id, emoji.emojize(f'🌍 В г. {city} сейчас {w_res[2]}\n'
                                          f'🌡 Температура воздуха {w_res[0]} (ощущ. {w_res[1]})\n'
                                          f'💦 Влажность {w_res[-1]}\n'
                                                        f'💨 Скорость ветра {w_res[3]} м/с, направление {w_res[4]}'))

    answer(w_res)


bot.infinity_polling()
