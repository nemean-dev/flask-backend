import requests
from langcodes import Language
from flask_babel import _
from app import app

def translate(text, dest_lang):
    language = Language.make(dest_lang).display_name()
    print(language)
    if not app.config.get('OPENAI_API_KEY'):
        return _('Error: translation service is not configured.')

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {app.config['OPENAI_API_KEY']}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
        {
            "role": "system",
            "content": (
                f"You are a translator. You detect the input language and translate it to {language}. "
                # 'Your replies must be in the following format:'
                # f'`translated from <detected language>: <translation written in {language}>`'
                f"Your replies must be written in {language}. They consist of the translation of the user input; nothing else."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]
    }

    res = requests.post(url, headers=headers, json=data)
    if res.status_code != 200:
        return _('Error: the translation service failed.')

    answer = res.json()["choices"][0]["message"]["content"]

    return answer
