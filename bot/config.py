from datetime import datetime

import telebot

from environs import Env

from read import read_lessons

env = Env()
env.read_env()

TOKEN = env.str('TOKEN')
GROUP_ID = env.int('GROUP_ID')
API_WEATHER = env.str('API_WEATHER')
CITY = env.str('CITY')
WEATHER_TIME = env.str('WEATHER_TIME')
SCHEDULE_TIME = env.str('SCHEDULE_TIME')

bot = telebot.TeleBot(TOKEN)

cabinets_info = {"cabinets": [], "author": ''}

schedule = read_lessons('bot/data/lessons.txt')

start_lessons = datetime(2023, 9, 4)
