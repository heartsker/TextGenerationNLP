import os
import json

raw = open('raw.json', 'r', encoding = 'utf-8')
messages = open('messages.json', 'w', encoding = 'utf-8')
data = json.load(raw)

result = {'messages': []}

for message in data['messages']:
    
    skip = False

    for submes in list(message['text']):
        if 'type' in submes:
            skip = True
            break

    if skip:
        continue
    text = message['text']

    if 'sticker_emoji' in message:
        text += message['sticker_emoji']
    
    if text == '' or not 'from' in message:
        continue

    user = 1 if message['from'] == 'Daniel Pustotin' else 0
    result['messages'].append({'from': user, 'text': str(text).lower()})

json.dump(result, messages, ensure_ascii=False)