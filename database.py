import sqlite3
import logging


def change_db(sql):
    cursor.execute(sql)


def get_from_db(sql):
    result = cursor.execute(sql).fetchall()
    return result


def user_in_db(user_id):
    res = get_from_db(f'SELECT * FROM questions WHERE user_id = {user_id};')
    return res


def add_user(user_id):
    if not user_in_db(user_id):
        change_db(f'INSERT INTO questions (user_id) VALUES ({user_id});')
        logging.info(f'Добавлен пользователь {user_id}')


def reset_assistant(user_id):
    sql = f'UPDATE questions SET answer = "" WHERE user_id = {user_id};'
    change_db(sql)


def set_param(param, value, user_id):
    sql = f'UPDATE questions SET {param} = "{value}" WHERE user_id = {user_id};'
    change_db(sql)


def get_params(user_id):
    sql = f'SELECT subject, level, answer FROM questions WHERE user_id = {user_id};'
    return get_from_db(sql)


def update_assistant(new_answer, user_id):
    current_assistant = get_params(user_id)[0][2]
    sql = f'UPDATE questions SET answer = "{current_assistant + new_answer}" WHERE user_id = {user_id};'
    change_db(sql)


def close_db():
    cursor.close()
    connection.close()


connection = sqlite3.connect('db.sqlite', check_same_thread=False)
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    subject TEXT,
    level INTEGER,
    question TEXT,
    answer TEXT
);
''')
