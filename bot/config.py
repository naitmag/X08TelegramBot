import telebot

from environs import Env

env = Env()
env.read_env()

TOKEN = env.str('TOKEN')
GROUP_ID = env.int('GROUP_ID')
API_WEATHER = env.str('API_WEATHER')
CITY = env.str('CITY')
WEATHER_TIME = env.str('WEATHER_TIME')

bot = telebot.TeleBot(TOKEN)

cabinets_info = {"cabinets": [], "author": ''}
