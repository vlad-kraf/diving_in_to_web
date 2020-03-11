import telebot
from telebot import types
from config import token

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, """
Howdy, how are you doing? There is a list of commands:
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
    chat_id = message.chat.id
    bot.send_message(chat_id, f"message: {message}, data: {data}")


@bot.message_handler(commands=['show_keyboard'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup()
    btn_help = types.KeyboardButton('/help')
    btn_add = types.KeyboardButton('/add')
    btn_list = types.KeyboardButton('/list')
    btn_rest = types.KeyboardButton('/reset')
    btn_btns_off = types.KeyboardButton('/hide_keyboard')

    markup.row(btn_add, btn_list, btn_rest)
    markup.row(btn_help, btn_btns_off)

    chat_id = message.chat.id
    bot.send_message(chat_id, "Choose one letter:", reply_markup=markup)


@bot.message_handler(commands=['hide_keyboard'])
def send_welcome(message):
    markup = types.ReplyKeyboardRemove()
    chat_id = message.chat.id
    bot.send_message(chat_id, "Commands keyboard removed", reply_markup=markup)


@bot.callback_query_handler(func=lambda x: True)
def button_handler(callback_query):
    print("22222")
    message = callback_query.message
    data = callback_query.data
    chat_id = message.chat.id
    bot.send_message(chat_id, f"message: {callback_query}, data: {data}")


@bot.message_handler(commands=['echo'])
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()
