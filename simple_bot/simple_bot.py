from collections import defaultdict
from telebot import TeleBot, types
from config import token
import redis
import os

bot = TeleBot(token)
"""
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True)
#r = redis.from_url(redis_url, db=0, decode_responses=True)
"""
pool = redis.ConnectionPool(host='localhost', port=6379, db=0, decode_responses=True)
r = redis.Redis(connection_pool=pool)


def write_title_to_redis(message):
    user_id = message.chat.id
    location_title = message.text
    r.lpush(user_id, location_title)


def write_coords_to_redis(user_id, location):
    lat, lon = location.latitude, location.longitude
    title = r.lpop(user_id)
    full_location_data = f'{title}&#124;{lat}&#124;{lon}'
    r.lpush(user_id, full_location_data)


def delete_location(user_id):
    r.lpop(user_id)


# User`s states.
START, NEUTRAL, ADD_NAME, ADD_LOCATION, ADD_IMAGE, CONFIRMATION = range(6)
USER_STATE = defaultdict(lambda: NEUTRAL)

# texts for greetings and list of available commands.
commands_list = """
There is a list of commands, that you can use:
/help - shows all the commands.
/add - adds the point.
/list - shows a list of recently added points.
/reset - removes all saved data.
/hide_keyboard - hides additional keyboard.
/show_keyboard - shows additional keyboard.\n
"""

greeting_text = 'Howdy, how are you doing? \n'

notice_text = 'Additional keyboard is shown to simplify input of commands.\n'


# get current user`s state.
def get_state(message):
    return USER_STATE[message.chat.id]


# update current user`s state.
def update_state(message, state):
    USER_STATE[message.chat.id] = state


# cancel bottom to interrupt operation.
def cancel_button():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    keyboard.add(*buttons)
    return keyboard


# cancel bottom to interrupt operation.
def comfirmation_button():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text='Yes', callback_data='confirm'),
               types.InlineKeyboardButton(text='No', callback_data='cancel')]
    keyboard.add(*buttons)
    return keyboard


# returns additional keyboard with commands
def additional_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    btn_help = types.KeyboardButton('/help')
    btn_add = types.KeyboardButton('/add')
    btn_list = types.KeyboardButton('/list')
    btn_rest = types.KeyboardButton('/reset')
    btns_off = types.KeyboardButton('/hide_keyboard')

    keyboard.row(btn_add, btn_list, btn_rest)
    keyboard.row(btn_help, btns_off)
    return keyboard


# checking if current command interrupt process of adding name of place, location or picture.
def interrupt_check(message):
    if get_state(message) in [ADD_NAME, ADD_LOCATION, ADD_IMAGE, CONFIRMATION]:
        bot.send_message(message.chat.id, text='Process of adding a place was interrupted, please try again')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    interrupt_check(message)

    update_state(message, NEUTRAL)
    keyboard = additional_keyboard()
    bot.send_message(message.chat.id, greeting_text+notice_text+commands_list, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    interrupt_check(message)

    update_state(message, NEUTRAL)
    bot.send_message(message.chat.id, commands_list)


@bot.callback_query_handler(func=lambda x: True)
def button_handler(callback_query):
    message = callback_query.message
    data = callback_query.data
    if data == 'cancel':
        update_state(message, NEUTRAL)
        delete_location(message.chat.id)
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)
        bot.send_message(message.chat.id, text="Process of adding a place was canceled.")
    elif data == 'confirm':
        update_state(message, NEUTRAL)
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)
        bot.send_message(message.chat.id, text="New Place was added.")


@bot.message_handler(commands=['show_keyboard'])
def send_welcome(message):
    interrupt_check(message)

    keyboard = additional_keyboard()
    bot.send_message(
        message.chat.id,
        "Keyboard shown. You cat turn it off any time by command /hide_keyboard.",
        reply_markup=keyboard)


@bot.message_handler(commands=['hide_keyboard'])
def send_welcome(message):
    interrupt_check(message)

    markup = types.ReplyKeyboardRemove()
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Keyboard hidden. You can turn it on in any time by command /show_keyboard.",
        reply_markup=markup)


# Chat commands:

# Initiation of the adding new place.
@bot.message_handler(commands=['add'])
def echo_all(message):
    interrupt_check(message)

    update_state(message, ADD_NAME)
    cancel = cancel_button()
    bot.send_message(message.chat.id, text='Please, type the name of new place or cancel the operation.',
                     reply_markup=cancel)


# Showing the list of recently added places.
@bot.message_handler(commands=['list'])
def echo_all(message):
    interrupt_check(message)

    update_state(message, NEUTRAL)

    last_locations = r.lrange(message.chat.id, 0, 10)
    print (last_locations)
    if len(last_locations) == 0:
        bot.send_message(chat_id=message.chat.id, text='There are no locations')
    else:
        bot.send_message(message.chat.id, text='List of recently added places:')
        for location in last_locations:
            if '&#124;' in location:

                title, lat, lon = location.split('&#124;')
                bot.send_message(chat_id=message.chat.id, text=title)
                bot.send_location(message.chat.id, lat, lon)
            else:
                bot.send_message(chat_id=message.chat.id, text=location)


# Removing all users data.
@bot.message_handler(func=lambda x: True, commands=['reset'])
def handle_confirmation(message):
    r.flushdb()
    bot.send_message(chat_id=message.chat.id, text='All places is removed.')


# Step 1: handling the name of the place.
@bot.message_handler(func=lambda message: get_state(message) == ADD_NAME)
def echo_all(message):
    if '/' not in message.text:
        write_title_to_redis(message)
        update_state(message, ADD_LOCATION)
        cancel = cancel_button()
        bot.send_message(chat_id=message.chat.id, text='Please, send your location or cancel the operation.',
                         reply_markup=cancel)
    else:
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
        update_state(message, START)


# Step 2: handling location.
@bot.message_handler(func=lambda message: get_state(message) == ADD_LOCATION, content_types=['location'])
def handle_location(message):
    print("Location: ", message.location)
    if message.text is None or '/' not in message.text: # Переделать проверку локации.
        write_coords_to_redis(message.chat.id, message.location)

        update_state(message, CONFIRMATION)
        keyboard = comfirmation_button()
        bot.send_message(chat_id=message.chat.id, text='Do you want to add new location?',
                         reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
        update_state(message, START)


bot.polling()
