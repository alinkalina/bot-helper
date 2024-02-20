import telebot
from config import token
from gpt import ask_gpt


bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'hi')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'helping')


def get_prompt(prompt):
    bot.send_message(prompt.chat.id, ask_gpt(prompt.text))


@bot.message_handler(commands=['ask'])
def ask_message(message):
    msg = bot.send_message(message.chat.id, 'print answer')
    bot.register_next_step_handler(msg, get_prompt)


bot.polling()
