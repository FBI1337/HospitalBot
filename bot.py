from telebot import TeleBot
from structure import register_handlers

API_TOKEN = '7000708851:AAHy3Kx7Vw8GKB_HbLPgWyuNEjYZRmKgQAw'

bot = TeleBot(API_TOKEN)

# Регистрируем все хендлеры
register_handlers(bot)

# Запуск бота
bot.polling()
