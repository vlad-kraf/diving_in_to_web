from telebot import TeleBot, types
#from config import token
import redis
import os

token = os.getenv('TOKEN')
bot = TeleBot(token)
USERS = {}

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


class BotError(Exception):
    pass


class RedisConnector:
    """Class encapsulates connection to Redis and methods of interaction with db, that necessary for ChatBot"""

    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis = redis.from_url(self.redis_url, db=0, decode_responses=True)

    def add_place(self, message, title, location):
        lat, lon = location.latitude, location.longitude
        data = f'{title}&#124;{lat}&#124;{lon}'
        self.redis.lpush(message.chat.id, data)

    def remove_all_places(self, message):
        self.redis.delete(message.chat.id)

    def get_last_locations(self, message):
        return self.redis.lrange(message.chat.id, 0, 10)


red = RedisConnector()


class User:
    """Class that describes user object and it's methods"""

    def __init__(self, message):
        self.user_id = message.chat.id
        self.state = 'NEUTRAL'
        self.new_place = ''
        self.new_location = {}
        self.available_states = ('NEUTRAL', 'ADD_NAME', 'ADD_LOCATION', 'ADD_IMAGE', 'CONFIRMATION')

    def get_state(self):
        return self.state

    def update_state(self, new_state):
        if new_state in self.available_states:
            self.state = new_state
        else:
            raise BotError("There is not such state")


#####################################################################################################
#                                           Block Keyboards                                         #
#####################################################################################################

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


#####################################################################################################
#                                           Block TeleBot functions                                 #
#####################################################################################################

@bot.callback_query_handler(func=lambda x: True)
def confirmation_handler(callback_query):
    message = callback_query.message
    data = callback_query.data
    if data == 'cancel':
        USERS[message.chat.id].new_location = {}
        USERS[message.chat.id].new_place = ''
        USERS[message.chat.id].update_state('NEUTRAL')

        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)
        bot.send_message(message.chat.id, text="Process of adding a place was canceled.")
    elif data == 'confirm':
        USERS[message.chat.id].update_state('NEUTRAL')
        red.add_place(message, USERS[message.chat.id].new_place, USERS[message.chat.id].new_location)
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)
        bot.send_message(message.chat.id, text="New Place was added.")


@bot.message_handler(commands=['start'])
def command_start(message):
    if message.chat.id not in USERS:
        USERS[message.chat.id] = User(message)

    USERS[message.chat.id].update_state('NEUTRAL')
    keyboard = additional_keyboard()
    bot.send_message(message.chat.id, greeting_text+notice_text+commands_list, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def command_help(message):
    USERS[message.chat.id].update_state('NEUTRAL')
    bot.send_message(message.chat.id, commands_list)


@bot.message_handler(commands=['show_keyboard'])
def command_show_keyboard(message):
    keyboard = additional_keyboard()
    bot.send_message(
        message.chat.id,
        "Keyboard shown. You cat turn it off any time by command /hide_keyboard.",
        reply_markup=keyboard)


@bot.message_handler(commands=['hide_keyboard'])
def command_hide_keyboard(message):
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id,
                     "Keyboard hidden. You can turn it on in any time by command /show_keyboard.",
                     reply_markup=markup)


# Chat commands:

# Initiation of the adding new place.
@bot.message_handler(commands=['add'])
def command_add(message):
    USERS[message.chat.id].update_state('ADD_NAME')
    cancel = cancel_button()
    bot.send_message(message.chat.id,
                     text='Please, type the name of new place or cancel the operation.',
                     reply_markup=cancel)


# Showing the list of recently added places.
@bot.message_handler(commands=['list'])
def command_list(message):
    USERS[message.chat.id].update_state('NEUTRAL')
    last_locations = red.get_last_locations(message)

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
def command_reset(message):
    red.remove_all_places(message)
    bot.send_message(chat_id=message.chat.id, text='All places is removed.')


# Step 1: handling the name of the place.
@bot.message_handler(func=lambda message: USERS[message.chat.id].get_state() == 'ADD_NAME')
def echo_all(message):
    if '/' not in message.text:
        USERS[message.chat.id].new_place = message.text
        USERS[message.chat.id].update_state('ADD_LOCATION')
        cancel = cancel_button()
        bot.send_message(chat_id=message.chat.id,
                         text='Please, send your location or cancel the operation.',
                         reply_markup=cancel)
    else:
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
        USERS[message.chat.id].update_state('NEUTRAL')


# Step 2: handling location.
@bot.message_handler(func=lambda message: USERS[message.chat.id].get_state() == 'ADD_LOCATION',
                     content_types=['location'])
def handle_location(message):
    if message.text is None or '/' not in message.text:
        USERS[message.chat.id].new_location = message.location
        USERS[message.chat.id].update_state('CONFIRMATION')
        keyboard = comfirmation_button()
        bot.send_message(chat_id=message.chat.id, text='Do you want to add new location?',
                         reply_markup=keyboard)
    else:
        bot.send_message(chat_id=message.chat.id, text='Добавление прервано')
        USERS[message.chat.id].update_state('START')


if __name__ == '__main__':
    bot.polling()
