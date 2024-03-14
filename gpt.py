import logging
import requests


url = 'http://localhost:1234/v1/chat/completions'
headers = {'Content-Type': 'application/json'}
json = {
        'messages': [],
        'temperature': 1.2,
        'max_tokens': 2000
    }


def create_json(question, subject, level, assistant):
    if assistant:
        json['messages'].append({'role': 'assistant', 'content': assistant})
    else:
        json['messages'] = []
        json['messages'].append({'role': 'user', 'content': question})
        json['messages'].append({'role': 'system', 'content': f'Очень кратко ответь на русском языке на вопрос по '
                                                              f'предмету {subject} как будто ты объясняешь человеку, '
                                                              f'который в этом {level}:'})


def ask_gpt(question, params):
    subject, level, assistant = params
    create_json(question, subject, level, assistant)
    try:
        resp = requests.post(url, headers=headers, json=json)
        if resp.status_code == 200 and 'choices' in resp.json():
            try:
                del json['messages'][2]
            except IndexError:
                pass
            logging.info(f"Ответ:\n{resp.json()['choices'][0]['message']['content']}")
            return resp.json()['choices'][0]['message']['content']
        else:
            logging.error('Ошибка НЕ 200')
            return 'Похоже, с нейросетью какие-то проблемы. Но не волнуйтесь, скоро их устранят, и Вы сможете снова ' \
                   'задать свой вопрос'
    except requests.exceptions.ConnectionError:
        logging.critical('Нет соединения с нейросетью')
        return 'Похоже, у бота пропало соединения с нейросетью. Повторите попытку через некоторое время'
