import requests


class GPT:
    def __init__(self):
        self.url = 'http://localhost:1234/v1/chat/completions'
        self.headers = {'Content-Type': 'application/json'}
        self.json = {
                'messages': [
                    {'role': 'system', 'content': 'По-русски кратко ответь на вопрос: '},
                ],
                'temperature': 1.2,
                'max_tokens': 2000
            }
        self.assistant = ''

    def create_json(self, question):
        self.json['messages'].append({'role': 'user', 'content': question})
        if self.assistant:
            self.json['messages'].append({'role': 'assistant', 'content': self.assistant})

    def ask_gpt(self, question):
        self.create_json(question)
        try:
            resp = requests.post(self.url, headers=self.headers, json=self.json)
            if resp.status_code == 200 and 'choices' in resp.json():
                self.assistant = self.assistant + resp.json()['choices'][0]['message']['content']
                del self.json['messages'][1]
                try:
                    del self.json['messages'][1]
                except IndexError:
                    pass
                return resp.json()['choices'][0]['message']['content']
            else:
                return 'error'
        except requests.exceptions.ConnectionError:
            return 'error'
