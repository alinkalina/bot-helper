import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from gpt import GPT
from config import token


bot = telebot.TeleBot(token)
users = {}


def add_user(chat_id):
    if chat_id not in users.keys():
        users[chat_id] = GPT()


@bot.message_handler(commands=['start'])
def start_message(message):
    add_user(message.chat.id)
    bot.send_message(message.chat.id, 'hi')


@bot.message_handler(commands=['help'])
def help_message(message):
    add_user(message.chat.id)
    bot.send_message(message.chat.id, 'helping')


def get_prompt(prompt):
    if not prompt.text.startswith('/'):
        msg = bot.send_message(prompt.chat.id, 'wait')
        markup = ReplyKeyboardMarkup().add(KeyboardButton('Продолжи'))
        answer = users[prompt.chat.id].ask_gpt(prompt.text)
        bot.delete_message(prompt.chat.id, msg.id)
        bot.send_message(prompt.chat.id, answer, reply_markup=markup)


@bot.message_handler(commands=['ask'])
def ask_message(message):
    add_user(message.chat.id)
    users[message.chat.id].assistant = ''
    msg = bot.send_message(message.chat.id, 'print answer')
    bot.register_next_step_handler(msg, get_prompt)


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text == 'Продолжи':
        get_prompt(message)


bot.infinity_polling()
