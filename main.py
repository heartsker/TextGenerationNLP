from telegram import *
from telegram.ext import *
import engine
from dotenv import load_dotenv
import os
import strings
import random
import json
from datetime import datetime

# load API_KEY
load_dotenv()
API_KEY = os.getenv('API_KEY')

# global variables
nlp_context = ''
nlp_question = ''
is_choosing = False
is_stopped = False
history = []

# handlers
def reply(update, text):
    global history

    history.append({'bot' : text })
    update.message.reply_text(text)

def did_not_understand(update, context):
    if is_stopped:
        reply(update, strings.stopped)
    else:
        reply(update, strings.did_not_understand)

def choose_next(update, context):
    buttons = [[KeyboardButton(strings.next_context)], [KeyboardButton(strings.next_question)]]
    context.bot.send_message(chat_id = update.effective_chat.id, text = strings.choose_next, reply_markup = ReplyKeyboardMarkup(buttons))

def start_command(update, context):
    global is_stopped
    global nlp_context
    global nlp_question
    global is_choosing

    nlp_context = ''
    nlp_question = ''
    is_choosing = False
    is_stopped = False

    reply(update, strings.indroduction.format(update.message.chat.first_name))
    reply(update, strings.gimmy_context)

def quit_command(update, context):
    global is_stopped

    if is_stopped:
        reply(update, strings.stopped_already)
    else:
        is_stopped = True
        reply(update, strings.goodbye)

def export_command(update, context):
    global history

    history.append( {update.message.chat.username : '📤 Exported the history'} )

    dump = json.dumps(history, indent=4)
    now = datetime.now()
    time = now.strftime("%H-%M-%S")

    with open('history-{}-{}.json'.format(update.message.chat.username, time), 'w') as outfile:
        outfile.write(dump)

def info_command(update, context):
    global history

    history.append( {update.message.chat.username : '/info'})

    reply(update, strings.info)

def handle_message(update, context):
    global nlp_context
    global nlp_question
    global is_choosing
    global is_stopped
    global history

    message = update.message.text

    history.append({ update.message.chat.username: message })

    if is_stopped:
        did_not_understand(update, context)

    # if choosing new question or context
    if is_choosing:
        if message in strings.next_context:
            nlp_context = ''
            is_choosing = False
            reply(update, strings.provide_context)
        elif message in strings.next_question:
            nlp_question = ''
            is_choosing = False
            reply(update, strings.provide_question)
        else:
            did_not_understand(update, context)
    else:
        # if reading new question or context
        if nlp_context == '':
            nlp_context = message
            nlp_question = ''
            reply(update, strings.gimmy_question)
        elif nlp_question == '':
            nlp_question = message

        # if ready to answer
        if nlp_context != '' and nlp_question != '':
            response = engine.response(nlp_question, nlp_context)
            if response == '':
                response = strings.no_answer
            else:
                response = random.choice(strings.answer_intros) + ' ' + response
            reply(update, response)
            nlp_question = ''
            is_choosing = True
            choose_next(update, context)

def error(update, context):
    print(f"Update {update} caused an error {context.error}")

# main part
def prepare():
    engine.prepare()

def main():
    print("heartsker_qa_bot started")
    updater = Updater(API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('quit', quit_command))
    dispatcher.add_handler(CommandHandler('export', export_command))
    dispatcher.add_handler(CommandHandler('info', info_command))
    
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

prepare()
main()