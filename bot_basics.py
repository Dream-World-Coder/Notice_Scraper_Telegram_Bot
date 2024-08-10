import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


# reading the token here, using os module, also use: "source .env" cmd in terminal
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)



########################## 
# handling commands
##########################

# @bot.message_handler(commands=['start', 'hello'])
# def hello(message):
#     bot.reply_to(message, 'Hello, I am s-bot')




###########################
# echo anything
##########################

# @bot.message_handler(func=lambda message:True)
# def echo_all(message):
#     msg = f'{message.text}\nFor commands use: /<cmds>'
#     bot.reply_to(message, msg)





###########################
# callback 
##########################

# @bot.message_handler(commands=['play'])
# def play(message):
#     text = "so what game do you want to play? GuessTheNumber or GameTheory"
#     sent_msg = bot.send_game(message.chat.id, text, parse_mode="Markdown")
#     bot.register_next_step_handler(sent_msg, callback=None)
    



###########################
# MENU MAKING
##########################

# inside chat
# @bot.message_handler(commands=['start', 'menu'])
# def send_welcome(message):
#     markup = InlineKeyboardMarkup()
#     markup.add(InlineKeyboardButton("Option 1", callback_data="option1"))
#     markup.add(InlineKeyboardButton("Option 2", callback_data="option2"))
#     markup.add(InlineKeyboardButton("Option 3", callback_data="option3"))
#     bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: True)
# def handle_query(call):
#     if call.data == "option1":
#         bot.send_message(call.message.chat.id, "You selected Option 1")
#     elif call.data == "option2":
#         bot.send_message(call.message.chat.id, "You selected Option 2")
#     elif call.data == "option3":
#         bot.send_message(call.message.chat.id, "You selected Option 3")






###########################
# inside input box/ msg box or phone keyboard of telegram
##########################

# @bot.message_handler(commands=['start', 'menu'])
# def send_welcome(message):
#     markup = ReplyKeyboardMarkup(row_width=2)
#     btn1 = KeyboardButton("Option 1")
#     btn2 = KeyboardButton("Option 2")
#     btn3 = KeyboardButton("Option 3")
#     markup.add(btn1, btn2, btn3)
#     bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     if message.text == "Option 1":
#         bot.send_message(message.chat.id, "You selected Option 1")
#     elif message.text == "Option 2":
#         bot.send_message(message.chat.id, "You selected Option 2")
#     elif message.text == "Option 3":
#         bot.send_message(message.chat.id, "You selected Option 3")



###########################
# back button
##########################

# Main menu
def main_menu():
    markup = ReplyKeyboardMarkup(row_width=2)
    btn1 = KeyboardButton("Option 1")
    btn2 = KeyboardButton("Option 2")
    btn3 = KeyboardButton("Option 3")
    markup.add(btn1, btn2, btn3)
    return markup

# Sub-menu for Option 1
def submenu_option1():
    markup = ReplyKeyboardMarkup(row_width=1)
    back_btn = KeyboardButton("Back")
    markup.add(back_btn)
    return markup

# Command handler for /start and /menu
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=main_menu())

# General message handler
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Option 1":
        bot.send_message(message.chat.id, "You selected Option 1", reply_markup=submenu_option1())
    elif message.text == "Option 2":
        bot.send_message(message.chat.id, "You selected Option 2", reply_markup=submenu_option1()) # Assuming same submenu for simplicity
    elif message.text == "Option 3":
        bot.send_message(message.chat.id, "You selected Option 3", reply_markup=submenu_option1()) # Assuming same submenu for simplicity
    elif message.text == "Back":
        bot.send_message(message.chat.id, "Back to main menu", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Invalid option. Choose an option:", reply_markup=main_menu())




# to start the bot
bot.infinity_polling()