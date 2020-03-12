from collections import defaultdict
from telebot import TeleBot, types
from config import token

bot = TeleBot(token)

START, NEUTRAL, ADD_NAME, ADD_LOCATION, ADD_PICTURE, CONFIRMATION = range(6)
USER_STATE = defaultdict(lambda: NEUTRAL)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text='Cancel', callback_data='cancel')]
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    update_state(message, NEUTRAL)
    bot.send_message(message.chat.id, """
Howdy, how are you doing? 

There is a list of commands, that you can use:
/help - shows all commands
/add - adds the point
/list - shows a list of recently added points
/reset - removes all saved data
/hide_keyboard - hides keyboard with commands
/show_keyboard - shows keyboard with commands
""")


@bot.callback_query_handler(func=lambda x: True)
def button_handler(callback_query):
    message = callback_query.message
    data = callback_query.data
    if data == 'cancel':
        update_state(message, NEUTRAL)
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=None)
        bot.send_message(message.chat.id, text="Process of adding a place was interrupted, please try again")


@bot.message_handler(commands=['show_keyboard'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup()
    btn_help = types.KeyboardButton('/help')
    btn_add = types.KeyboardButton('/add')
    btn_list = types.KeyboardButton('/list')
    btn_rest = types.KeyboardButton('/reset')
    btns_off = types.KeyboardButton('/hide_keyboard')

    markup.row(btn_add, btn_list, btn_rest)
    markup.row(btn_help, btns_off)

    bot.send_message(
        message.chat.id,
        "Keyboard shown. You cat turn it off any time by command /hide_keyboard.",
        reply_markup=markup)


@bot.message_handler(commands=['hide_keyboard'])
def send_welcome(message):
    markup = types.ReplyKeyboardRemove()
    chat_id = message.chat.id
    bot.send_message(
        chat_id,
        "Keyboard hidden. You can turn it on in any time by command /show_keyboard.",
        reply_markup=markup)


# Chat commands:
@bot.message_handler(commands=['add'])
def echo_all(message):
    update_state(message, ADD_NAME)
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, text='Please, type the name of new place:',  reply_markup=keyboard)


@bot.message_handler(commands=['list'])
def echo_all(message):

    if get_state(message) in [ADD_NAME, ADD_LOCATION, ADD_PICTURE, CONFIRMATION]:
        bot.send_message(message.chat.id, text='Process of adding a place was interrupted, please try again')

    update_state(message, NEUTRAL)
    bot.send_message(message.chat.id, text='List of recently added places:')


@bot.message_handler(commands=['reset'])
def echo_all(message):

    if get_state(message) in [ADD_NAME, ADD_LOCATION, ADD_PICTURE, CONFIRMATION]:
        bot.send_message(message.chat.id, text='Process of adding a place was interrupted, please try again')

    update_state(message, NEUTRAL)
    bot.send_message(message.chat.id, text='All personal data were removed')


bot.polling()
