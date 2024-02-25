import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
    bot.send_message(message.chat.id, 'Здравствуйте! Это Математик - Ваш помощник в решении различных математических '
                                      'задач. Задавайте вопросы с помощью команды /ask, и бот пришлёт Вам ответ, '
                                      'сгенерированный с помощью нейросети. Правда, он англичанин, но учит русский '
                                      'язык, поэтому он будет стараться отвечать на Вашем языке, но ничего не обещает '
                                      ':) А также, из-за большой нагрузки ответы не всегда могут быть абсолютно '
                                      'точными, так что не советуем полагаться на них на 100%',
                     reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=['help'])
def help_message(message):
    add_user(message.chat.id)
    bot.send_message(message.chat.id, 'Вот какие команды здесь есть:\n'
                                      '/start - старт и немного инструкций\n'
                                      '/help - сообщение, которое Вы сейчас читаете\n'
                                      '/ask - задать вопрос', reply_markup=ReplyKeyboardRemove())


def get_prompt(prompt):
    if not prompt.text.startswith('/'):
        if len(prompt.text) > 1000:
            logging.warning(f'Запрос пользователя {prompt.chat.id} слишком длинный')
            msg = bot.send_message(prompt.chat.id, 'Извините, но Ваш запрос слишком длинный. Введите что-нибудь '
                                                   'покороче :)', reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, get_prompt)
        else:
            logging.info(f'От пользователя {prompt.chat.id} получен вопрос: {prompt.text}')
            msg = bot.send_message(prompt.chat.id, 'Подождите секундочку...', reply_markup=ReplyKeyboardRemove())
            markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Продолжи'))
            answer = users[prompt.chat.id].ask_gpt(prompt.text)
            bot.delete_message(prompt.chat.id, msg.id)
            try:
                bot.send_message(prompt.chat.id, answer, reply_markup=markup)
            except telebot.apihelper.ApiTelegramException:
                bot.send_message(prompt.chat.id, 'Объяснение закончено')
                logging.warning('От нейросети пришёл пустой ответ')
    else:
        logging.warning(f'Пользователь {prompt.chat.id} прервал вопрос командой {prompt.text}')


@bot.message_handler(commands=['ask'])
def ask_message(message):
    add_user(message.chat.id)
    logging.info(f'Пользователь {message.chat.id} начал задавать вопрос')
    users[message.chat.id].assistant = ''
    msg = bot.send_message(message.chat.id, 'Введите вопрос', reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_prompt)


@bot.message_handler(commands=['debug'])
def debugging(message):
    with open('logs.txt', 'r') as f:
        bot.send_document(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
    f.close()


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text == 'Продолжи':
        get_prompt(message)
    else:
        bot.send_message(message.chat.id, 'Вам следует воспользоваться командой или кнопкой, другого бот не понимает :('
                         , reply_markup=ReplyKeyboardRemove())


@bot.message_handler(content_types=['photo', 'audio', 'document', 'sticker', 'video', 'voice', 'location', 'contact'])
def error_message(message):
    bot.send_message(message.chat.id, 'Вам следует воспользоваться командой или кнопкой, другого бот не понимает :(',
                     reply_markup=ReplyKeyboardRemove())


try:
    logging.info('Бот запущен')
    bot.infinity_polling()
except Exception as e:
    logging.critical(f'Произошла ошибка: {e}')
