import telebot
import os
import requests
import json
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
API = WEATHER_API_KEY

user_settings = {}


@bot.message_handler(commands=['start']) #Приветствие
def intro(message):
    user_settings[message.chat.id] = {'lang': 'en','units': 'metric'}
    bot.send_message(message.chat.id , f'Привет, {message.from_user.first_name}.\nЯ Weather Bot, я умею присылать прогноз погоды.\n\n'
                                           f'Hi {message.from_user.first_name}.\nI am Weather Bot, I can send weather forecast.', )
    choosing_language_message(message)

def choosing_language_message(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('English','Русский')
    bot.send_message(message.chat.id, 'Пожалуйста, выберите язык\n\nPlease, choose a languange',reply_markup=markup)
    bot.register_next_step_handler(message,settings)

def settings(message):
    if message.text == 'English':
        user_settings[message.chat.id]['lang'] = 'en'
    elif message.text == 'Русский':
        user_settings[message.chat.id]['lang'] = 'ru'
    else:
        bot.send_message(message.chat.id, 'Repeat one more time\nПовторите еще раз')
        choosing_language_message(message)
        return
    units_check_message(message)

def units_check_message(message):
    markup= ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    if user_settings[message.chat.id]['lang'] == 'ru':
        markup.add('Метрические', "Английские")
        bot.send_message(message.chat.id, 'Выберите единицы измерения:', reply_markup=markup)
    else:
        markup.add('Metric', 'Imperial')
        bot.send_message(message.chat.id, 'Choose units:', reply_markup=markup)
    bot.register_next_step_handler(message, units_assign)

def units_assign(message):

    if message.text in ['Metric', 'Метрические']:
        user_settings[message.chat.id]['units'] = 'metric'
    elif message.text in ['Imperial', 'Английские']:
        user_settings[message.chat.id]['units'] = 'imperial'
    else:
        bot.send_message(message.chat.id, 'Повторите еще раз' if user_settings[message.chat.id]['lang'] == 'ru' else 'Repeat one more time')
        units_check_message(message)
        return

    if user_settings[message.chat.id]['lang'] == 'ru':
        bot.send_message(message.chat.id, 'Пожалуйста, введите город:')
    else:
        bot.send_message(message.chat.id, 'Please, enter the city:')

@bot.message_handler(content_types=['text'])
def get_weather(message):
    lang = user_settings[message.chat.id]['lang']
    units = user_settings[message.chat.id]['units']
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&lang={lang}&units={units}')
    if res.status_code == 200:
        data = json.loads(res.text)
        localtemp = data["main"]["temp"]
        if lang == 'ru':
            bot.reply_to(message, f'Погода сейчас: {localtemp}')
        elif lang == 'en':
            bot.reply_to(message, f'Weather now is: {localtemp}')
    else:
        bot.reply_to(message, "Город указан неверно" if lang == 'ru' else "City is incorrect")

bot.polling(none_stop=True)