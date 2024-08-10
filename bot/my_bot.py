'''
    workflow of /get_notice_by_date:
    1. get_notice_type
    2. get_date
    3. ask_keywords_choice and get_keywords if any
    
    workflow of /get_notice:
    1. get_notice_type
    2. get number of notices
'''



import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from iiest_scrape import IIEST

load_dotenv()
BOT_TOKEN = os.getenv('SBOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Bot token not found. Please set the 'SBOT_TOKEN' environment variable.")
bot = telebot.TeleBot(BOT_TOKEN)

obj = None
is_get_notice_called = False

is_get_notice_by_date_called = False
is_key_words_choices_asked = False
is_date_inputed = False

is_precise = True
keyword_list = []

# Helper function to split long messages
def split_message(message, max_length=4095):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

#  FUNCTIONS
# #################################################################

# /start and /hello
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    help_text = (
        "For actions use commands like:\n"
        "/start - Start the bot\n"
        "/hello - Say hello to the bot\n"
        "/get_notice - Get the latest notices\n"
        "/get_notice_by_date - Get notices by date\n\tInput the date in dd/mm/yyyy format like 4/6/2024.\n\tIf you dont remember the exact date use: n/n/yyyy or n/mm/yyyy.\n"
    )
    bot.reply_to(message, f'Hello, I am s-bot, I can Fetch your notices easily from IIEST Shibpur\'s website.\n{help_text}')


# /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "For actions use commands like:\n"
        "/start - Start the bot\n"
        "/hello - Say hello to the bot\n"
        "/get_notice - Get the latest notices\n"
        "/get_notice_by_date - Get notices by date\n\tInput the date in dd/mm/yyyy format like 4/6/2024.\n\tIf you dont remember the exact date use: n/n/yyyy or n/mm/yyyy.\n\tThis will give all the notices on that range of dates.\n"
        "/get_notice_by_date_unprecise - is_precise = False\n"
    )
    bot.reply_to(message, help_text)


# remove inline keyboard
def remove_inline_keyboard(chat_id, message_id):
    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=None)


# get notice type
def get_notice_type(message):
    markup = InlineKeyboardMarkup(row_width=2)
    notice_types = ['Admission', 'Employment', 'Tenders', 'Student', 'General', 'Finance', 'Placement', 'Faculty/Staff', 'CMS']
    for notice_type in notice_types:
        markup.add(InlineKeyboardButton(notice_type, callback_data=notice_type))
    bot.send_message(message.chat.id, 'What type of notice do you want?', reply_markup=markup)


# call back to options and print the input message
@bot.callback_query_handler(func=lambda call: call.data in ['Admission', 'Employment', 'Tenders', 'Student', 'General', 'Finance', 'Placement', 'Faculty/Staff', 'CMS'])
def handle_callback_query(call):
    bot.send_message(call.message.chat.id, f'Creating instance for {call.data} ...')
    notice_type = call.data   
    try:
        global obj, is_get_notice_called, is_get_notice_by_date_called
        obj = IIEST(notice_type)
        msg = None
        msg1 = 'Enter the number of latest notices you want to get.'
        msg2 = 'Enter date in DD/MM/YYYY format [use "/help" to know more uses].'
        if is_get_notice_called:
            msg = msg1
        elif is_get_notice_by_date_called or not is_precise:
            msg = msg2
        else:
            msg = "••••network••|•_•|•_•|••error••••"
        bot.send_message(call.message.chat.id, f'Instance created for {notice_type}.\n{msg}')
    except Exception as e:
        bot.send_message(call.message.chat.id, f'Error: {e}')
        if is_get_notice_called:
            is_get_notice_called = False
        elif is_get_notice_by_date_called:
            is_get_notice_by_date_called = False
        
    finally:
        remove_inline_keyboard(call.message.chat.id, call.message.message_id)


# /get_notice 
@bot.message_handler(commands=['get_notice'])
def get_notice(message):
    try:
        global is_get_notice_called
        is_get_notice_called = True
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    get_notice_type(message)


# fetch input the number when obj is created
@bot.message_handler(func=lambda message: message.text.isdigit() and obj is not None and is_get_notice_called and not is_get_notice_by_date_called)
def fetch_notices(message):
    global is_get_notice_called, obj
    num_notices = int(message.text)
    notices = obj.get_notice(num_notices)
    
    for part in split_message(notices):
        bot.send_message(message.chat.id, part)
    
    is_get_notice_called = False
    obj = None


# keyword or keywords
@bot.message_handler(func=lambda message: obj is not None and is_get_notice_by_date_called and is_date_inputed and is_key_words_choices_asked and not is_get_notice_called)
def get_keywords(message):
    try:
        global keyword_list, is_get_notice_by_date_called, is_date_inputed, is_key_words_choices_asked, obj, tup, is_precise
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    keyword_list = message.text.split(',')
    date = tup
    notices = obj.get_notice_by_date(day=date[0], month=date[1], year=date[2], keywords=tuple(keyword_list), isprecise=is_precise)
    
    if not len(notices) == 0:
        try:
            for part in split_message(notices):
                bot.send_message(message.chat.id, part)
        except Exception as e:
            bot.send_message(message.chat.id, f'Error: {e}')
    else:
        bot.send_message(message.chat.id, 'No notices found.')
        
    is_get_notice_by_date_called = False
    is_date_inputed = False
    is_key_words_choices_asked = False
    obj = None
    is_precise = True


# @bot.message_handler(func=lambda message: obj is not None and is_get_notice_by_date_called and is_date_inputed)
# this condition is true, i checked using vars. then why bruh why are u not called?
def ask_keywords_choice(message):
    try:
        global is_key_words_choices_asked
        is_key_words_choices_asked = True
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
        
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Yes', callback_data='keywords_present', row_width=1)
    btn2 = InlineKeyboardButton('No', callback_data='keywords_absent', row_width=1)
    markup.add(btn1,btn2)
    
    bot.send_message(message.chat.id, 'Do you want to add any keywords?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['keywords_present', 'keywords_absent'])
def handle_callback(call):
    if call.data == 'keywords_absent':
        global is_get_notice_by_date_called, is_date_inputed, is_key_words_choices_asked, obj, tup, is_precise
        date = tup
        notices = obj.get_notice_by_date(day=date[0], month=date[1], year=date[2], isprecise=is_precise)
        if not len(notices) == 0:
            try:
                for part in split_message(notices):
                    bot.send_message(call.message.chat.id, part)
            except Exception as e:
                bot.send_message(call.message.chat.id, f'Error: {e}')
        else:
            bot.send_message(call.message.chat.id, 'No notices found.')
        
        is_get_notice_by_date_called = False
        is_date_inputed = False
        is_key_words_choices_asked = False
        obj = None
        is_precise = True
        remove_inline_keyboard(call.message.chat.id, call.message.message_id)
        
    else:
        sent_msg = bot.send_message(call.message.chat.id, 'Enter keywords seperated by comma(,) only [No spaces, eg: a,b,c]: ')
        # bot.register_next_step_handler(sent_msg, callback = get_keywords(message=call.message))
        remove_inline_keyboard(call.message.chat.id, call.message.message_id)


# /get_notice_by_date
@bot.message_handler(commands=['get_notice_by_date'])
def get_notice_by_date(message):
    try:
        global is_get_notice_by_date_called
        is_get_notice_by_date_called = True
    except Exception as e:
        bot.send_message(message.chat.id, f'Error: {e}')
    get_notice_type(message)
    

# fetch value of date
@bot.message_handler(func=lambda message: obj is not None and is_get_notice_by_date_called  and '/' in message.text)
def fetch_date(message):
    global is_date_inputed
    is_date_inputed = True
    
    date = message.text.strip()
    
    dt = date.split('/')
    # print(dt)
    # bcz it converts to int unlike html forms
    day = str(dt[0])
    month = str(dt[1])
    year = str(dt[2])
    
    day = None if not day.isdigit() else int(day)
    month = None if not month.isdigit() else int(month)
    year = None if not year.isdigit() else int(year)
    
    # var = obj is not None and is_get_notice_by_date_called and is_date_inputed
    # print('\n\n\nvar: ', var)
    
    global tup
    tup =  day, month, year
    bot.send_message(message.chat.id, 'Date Stored.')
    ask_keywords_choice(message)


@bot.message_handler(commands=['get_notice_by_date_unprecise'])
def get_notice_by_date_unprecise(message):
    global is_precise 
    is_precise = False
    get_notice_by_date(message)

# default response, keep it in last
@bot.message_handler(func=lambda message: True)
def default_response(message):
    msg = (
        f'Message: {message.text} is not a command.\n\n'
        'For actions use commands like: /start, /hello, /get_notice, /get_notice_by_date, /get_notice_by_date_unprecise'
    )
    bot.reply_to(message, msg)


bot.infinity_polling()





'''
problems> slow


trend observed:
    kono kichu jodi appear korte hoi tahole function call korte hobe, like markups. 
    ar kono valu intake korte hole func=lambda use korte hobe. ar ota main func er pore bosate hobe
    
and, learnings:
    1. sequence ekta karon hote pare error er, jemon default_response() ta age thakar jonno golmal hochhilo.
    2. in python call by reference is rare, so use globals
    3. flag/marker gulo ekta state/dict er modhhe rakha jete pare.
    4. ar import kora function gulo je proper seta check korte hobe, jemon get_notice_by_date() nije kichu return na korai error aschilo.
    
    bot-making:
    basic str,
    input , out put, register, menu, call back, delete markup after input  etc


# @bot.message_handler(func=lambda message: obj is not None and is_get_notice_by_date_called and is_date_inputed)
# this condition is true, i checked using vars. then why bruh why are u not called?
def ask_keywords_choice(message):

    reason: these all functions here work on one input that is message sent by the user. Some thimes this messaeg can be an input to a function, sometimes they may trigger some commands
    etc. thats why while calling these functions, we need to pass the message as an argument. So the functions that take input can be always active using func , bcz we need to msg first 
    to give input and make them active. But when we need somrthing to appear without a message we need to call it explicitly, bcz othewise we need to send some msg to
    trigger the function. coz the msg chat id is different if i dont call it explicitly. 
'''