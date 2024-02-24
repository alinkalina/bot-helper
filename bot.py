import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import logging
from gpt import GPT
from config import token


bot = telebot.TeleBot(token)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='logs.txt', filemode='w')
users = {}


def add_user(chat_id):
    if chat_id not in users.keys():
        logging.info(f'Добавлен пользователь {chat_id}')
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
        if len(prompt.text) > 1000:
            logging.warning(f'Запрос пользователя {prompt.chat.id} слишком длинный')
            msg = bot.send_message(prompt.chat.id, 'too long')
            bot.register_next_step_handler(msg, get_prompt)
        else:
            logging.info(f'От пользователя {prompt.chat.id} получен вопрос: {prompt.text}')
            msg = bot.send_message(prompt.chat.id, 'wait')
            markup = ReplyKeyboardMarkup().add(KeyboardButton('Продолжи'))
            answer = users[prompt.chat.id].ask_gpt(prompt.text)
            bot.delete_message(prompt.chat.id, msg.id)
            bot.send_message(prompt.chat.id, answer, reply_markup=markup)
    else:
        logging.warning(f'Пользователь {prompt.chat.id} прервал вопрос командой {prompt.text}')


@bot.message_handler(commands=['ask'])
def ask_message(message):
    add_user(message.chat.id)
    logging.info(f'Пользователь {message.chat.id} начал задавать вопрос')
    users[message.chat.id].assistant = ''
    msg = bot.send_message(message.chat.id, 'print answer')
    bot.register_next_step_handler(msg, get_prompt)


@bot.message_handler(commands=['debug'])
def debugging(message):
    with open('logs.txt', 'r') as f:
        bot.send_document(message.chat.id, f)
    f.close()


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text == 'Продолжи':
        get_prompt(message)


try:
    logging.info('Бот запущен')
    bot.infinity_polling()
except Exception as e:
    logging.critical(f'Произошла ошибка: {e}')
