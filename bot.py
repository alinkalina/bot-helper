import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from gpt import ask_gpt
import logging
from database import add_user, reset_assistant, set_param, get_params, update_assistant
from config import token


bot = telebot.TeleBot(token)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='logs.txt', filemode='w')

subjects = ['Математика', 'Физика', 'Химия', 'Информатика', 'Русский язык']
levels = ['Новичок', 'Профи']


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
            set_param('question', prompt.text, prompt.chat.id)
            logging.info(f'От пользователя {prompt.chat.id} получен вопрос: {prompt.text}')
            msg = bot.send_message(prompt.chat.id, 'Подождите секундочку...', reply_markup=ReplyKeyboardRemove())
            markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Продолжи'))
            answer = ask_gpt(prompt.text, *get_params(prompt.chat.id))
            update_assistant(answer, prompt.chat.id)
            bot.delete_message(prompt.chat.id, msg.id)
            try:
                bot.send_message(prompt.chat.id, answer, reply_markup=markup)
            except:
                bot.send_message(prompt.chat.id, 'Объяснение закончено')
                logging.warning('От нейросети пришёл пустой ответ или ответ с кавычками')
    else:
        logging.warning(f'Пользователь {prompt.chat.id} прервал вопрос командой {prompt.text}')


@bot.message_handler(commands=['ask'])
def ask_message(message):
    add_user(message.chat.id)
    logging.info(f'Пользователь {message.chat.id} начал задавать вопрос')
    reset_assistant(message.chat.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for subject in subjects:
        markup.add(KeyboardButton(subject))
    bot.send_message(message.chat.id, 'Выберите предмет, по которому хотите задать вопрос', reply_markup=markup)


@bot.message_handler(commands=['debug'])
def debugging(message):
    with open('logs.txt', 'r') as f:
        bot.send_document(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
    f.close()


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text == 'Продолжи':
        get_prompt(message)
    elif message.text in subjects:
        set_param('subject', message.text, message.chat.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for level in levels:
            markup.add(KeyboardButton(level))
        bot.send_message(message.chat.id, 'Выберите уровень объяснения (от этого зависит насколько заумные слова '
                                          'будут в ответе)', reply_markup=markup)
    elif message.text in levels:
        set_param('level', message.text, message.chat.id)
        msg = bot.send_message(message.chat.id, 'Введите вопрос', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_prompt)
    else:
        bot.send_message(message.chat.id, 'Вам следует воспользоваться командой или кнопкой, другого бот не понимает :('
                         , reply_markup=ReplyKeyboardRemove())


@bot.message_handler(content_types=['photo', 'audio', 'document', 'sticker', 'video', 'voice', 'location', 'contact'])
def error_message(message):
    bot.send_message(message.chat.id, 'Вам следует воспользоваться командой или кнопкой, другого бот не понимает :(',
                     reply_markup=ReplyKeyboardRemove())


try:
    logging.info('Бот запущен')
    bot.polling()
except Exception as e:
    logging.critical(f'Произошла ошибка: {type(e).__name__} - {str(e)}')
