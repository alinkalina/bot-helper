import requests


def ask_gpt(question):
    resp = requests.post(
        'http://localhost:1234/v1/chat/completions',
        headers={"Content-Type": "application/json"},
        json={
            "messages": [
                {"role": "system", "content": "Кратко ответь на вопрос на русском"},
                {"role": "user", "content": question}
            ],
            "temperature": 1,
            'max_tokens': 2000
        }
    )
    try:
        if resp.status_code == 200 and 'choices' in resp.json():
            return resp.json()['choices'][0]['message']['content']
        else:
            return 'error'
    except:
        return 'error'
