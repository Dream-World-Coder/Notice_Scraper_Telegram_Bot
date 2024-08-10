import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.executor import start_polling
from iiest_scrape import IIEST

BOT_TOKEN = os.getenv('SBOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Bot token not found. Please set the 'SBOT_TOKEN' environment variable.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

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

# Start and hello commands
@dp.message_handler(commands=['start', 'hello'])
async def send_welcome(message: types.Message):
    help_text = (
        "For actions use commands like:\n"
        "/start - Start the bot\n"
        "/hello - Say hello to the bot\n"
        "/get_notice - Get the latest notices\n"
        "/get_notice_by_date - Get notices by date\n\tInput the date in dd/mm/yyyy format like 4/6/2024.\n\tIf you dont remember the exact date use: n/n/yyyy or n/mm/yyyy.\n"
    )
    await message.reply(f'Hello, I am s-bot, I can fetch your notices easily from IIEST Shibpur\'s website.\n{help_text}')

# Help command
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    help_text = (
        "For actions use commands like:\n"
        "/start - Start the bot\n"
        "/hello - Say hello to the bot\n"
        "/get_notice - Get the latest notices\n"
        "/get_notice_by_date - Get notices by date\n\tInput the date in dd/mm/yyyy format like 4/6/2024.\n\tIf you dont remember the exact date use: n/n/yyyy or n/mm/yyyy.\n\tThis will give all the notices on that range of dates.\n"
        "/get_notice_by_date_unprecise - is_precise = False\n"
    )
    await message.reply(help_text)

# Get notice type
async def get_notice_type(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    notice_types = ['Admission', 'Employment', 'Tenders', 'Student', 'General', 'Finance', 'Placement', 'Faculty/Staff', 'CMS']
    for notice_type in notice_types:
        markup.add(InlineKeyboardButton(notice_type, callback_data=notice_type))
    await message.answer('What type of notice do you want?', reply_markup=markup)

# Callback for notice type selection
@dp.callback_query_handler(lambda call: call.data in ['Admission', 'Employment', 'Tenders', 'Student', 'General', 'Finance', 'Placement', 'Faculty/Staff', 'CMS'])
async def handle_callback_query(call: types.CallbackQuery):
    await call.message.answer(f'Creating instance for {call.data} ...')
    notice_type = call.data   
    global obj
    try:
        obj = IIEST(notice_type)
        msg = None
        msg1 = 'Enter the number of latest notices you want to get.'
        msg2 = 'Enter date in DD/MM/YYYY format [use "/help" to know more uses].'
        if is_get_notice_called:
            msg = msg1
        elif is_get_notice_by_date_called:
            msg = msg2
        else:
            msg = "••••network••|•_•|•_•|••error••••"
        await call.message.answer(f'Instance created for {notice_type}.\n{msg}')
    except Exception as e:
        await call.message.answer(f'Error: {e}')
    finally:
        await call.message.edit_reply_markup(reply_markup=None)

# Get notice command
@dp.message_handler(commands=['get_notice'])
async def get_notice(message: types.Message):
    global is_get_notice_called
    is_get_notice_called = True
    await get_notice_type(message)

# Fetch input number when obj is created
@dp.message_handler(lambda message: message.text.isdigit() and obj is not None and is_get_notice_called and not is_get_notice_by_date_called)
async def fetch_notices(message: types.Message):
    global is_get_notice_called, obj
    num_notices = int(message.text)
    notices = obj.get_notice(num_notices)
    
    for part in split_message(notices):
        await message.answer(part)
    
    is_get_notice_called = False
    obj = None

# Handle keywords input
@dp.message_handler(lambda message: obj is not None and is_get_notice_by_date_called and is_date_inputed and is_key_words_choices_asked and not is_get_notice_called)
async def get_keywords(message: types.Message):
    global keyword_list, is_get_notice_by_date_called, is_date_inputed, is_key_words_choices_asked, obj, tup, is_precise
    keyword_list = message.text.split(',')
    date = tup
    notices = obj.get_notice_by_date(day=date[0], month=date[1], year=date[2], keywords=tuple(keyword_list), isprecise=is_precise)
    
    if notices:
        for part in split_message(notices):
            await message.answer(part)
    else:
        await message.answer('No notices found.')
        
    is_get_notice_by_date_called = False
    is_date_inputed = False
    is_key_words_choices_asked = False
    obj = None
    is_precise = True

# Ask for keyword choice
async def ask_keywords_choice(message: types.Message):
    global is_key_words_choices_asked
    is_key_words_choices_asked = True
    
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton('Yes', callback_data='keywords_present')
    btn2 = InlineKeyboardButton('No', callback_data='keywords_absent')
    markup.add(btn1, btn2)
    
    await message.answer('Do you want to add any keywords?', reply_markup=markup)

# Handle keyword choice callback
@dp.callback_query_handler(lambda call: call.data in ['keywords_present', 'keywords_absent'])
async def handle_callback(call: types.CallbackQuery):
    global is_get_notice_by_date_called, is_date_inputed, is_key_words_choices_asked, obj, tup, is_precise
    if call.data == 'keywords_absent':
        date = tup
        notices = obj.get_notice_by_date(day=date[0], month=date[1], year=date[2], isprecise=is_precise)
        if notices:
            for part in split_message(notices):
                await call.message.answer(part)
        else:
            await call.message.answer('No notices found.')
        
        is_get_notice_by_date_called = False
        is_date_inputed = False
        is_key_words_choices_asked = False
        obj = None
        is_precise = True
        await call.message.edit_reply_markup(reply_markup=None)
    else:
        await call.message.answer('Enter keywords separated by comma(,) only [No spaces, eg: a,b,c]:')
        await call.message.edit_reply_markup(reply_markup=None)

# Get notice by date command
@dp.message_handler(commands=['get_notice_by_date'])
async def get_notice_by_date(message: types.Message):
    global is_get_notice_by_date_called
    is_get_notice_by_date_called = True
    await get_notice_type(message)

# Fetch date value
@dp.message_handler(lambda message: obj is not None and is_get_notice_by_date_called and '/' in message.text)
async def fetch_date(message: types.Message):
    global is_date_inputed
    is_date_inputed = True
    
    date = message.text.strip().split('/')
    
    day = None if not date[0].isdigit() else int(date[0])
    month = None if not date[1].isdigit() else int(date[1])
    year = None if not date[2].isdigit() else int(date[2])
    
    global tup
    tup = day, month, year
    await message.answer('Date Stored.')
    await ask_keywords_choice(message)

# Get notice by date unprecise command
@dp.message_handler(commands=['get_notice_by_date_unprecise'])
async def get_notice_by_date_unprecise(message: types.Message):
    global is_precise 
    is_precise = False
    await get_notice_by_date(message)

# Default response
@dp.message_handler(lambda message: True)
async def default_response(message: types.Message):
    msg = (
        f'Message: {message.text} is not a command.\n\n'
        'For actions use commands like: /start, /hello, /get_notice, /get_notice_by_date, /get_notice_by_date_unprecise'
    )
    await message.reply(msg)

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)
