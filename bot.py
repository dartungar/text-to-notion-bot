import os
import telebot
from notion.client import NotionClient
from notion.block import TextBlock

#tokens TODO delete Notion Noket from here
BOT_TOKEN = os.environ['BOT_TOKEN']
#NOTION_TOKEN = None #os.environ['NOTION_TOKEN']


#create bot
bot = telebot.TeleBot(BOT_TOKEN)

#lame disct for storing users
users = {}

#globals TODO fix this shit (with user dictionary?)
#page_address = None
#notion_client = None

basic_keyboard = telebot.types.ReplyKeyboardMarkup(True)
btn1 = telebot.types.KeyboardButton('/start')
btn2 = telebot.types.KeyboardButton('/help')
btn3 = telebot.types.KeyboardButton('/setclient')
btn4 = telebot.types.KeyboardButton('/checkclient')
btn5 = telebot.types.KeyboardButton('/setpage')
btn6 = telebot.types.KeyboardButton('/checkpage')
basic_keyboard.row(btn1, btn2, btn3)
basic_keyboard.row(btn4, btn5, btn6)


# TODO: более элегантное решение с диктами
@bot.message_handler(commands=['start', 'go', 'activate'])
def start_handler(message):
    username = message.from_user.username
    users[username] = {'name': username}
    bot.send_message(message.chat.id, 
    f'''Hey there, {username}! 
    I\'m a deadpan simple bot for appending text to Notion page.
    Get your "Notion API key" (go to any page in your Notion.so and look for "token_v2" in cookies). 
    Set your Notion Client with /setclient.
    Set page address with /setpage. 
    Then just send me text you want to appear on Notion page you set.''', 
    reply_markup=basic_keyboard)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, 
    f'''In order to send stuff to Notion, you need to get your 'internal API key' for Notion.

    1. go to any of your notion.so pages in browser
    2. press F12 / open developer tools 
    3. go to Application (Chrome) / Storage (Firefox) → cookies
    4. select https://www.notion.so
    5. find a cookie with name 'token_v2'
    6. copy its value
    7. use /setclient command and pass token_v2 to this bot
    8. choose Notion page to which you want send text, copy its URL
    9. use /setpage and send URL to bot

    Now any text you send to bot (except for commands) will be appended to Notion page you chose!
    ''', 
    reply_markup=basic_keyboard)



@bot.message_handler(commands=['setclient'])
def setclient_handler(message):
    username = message.from_user.username
    if username == 'dartungar':
        users[username]['notion_api_token'] = os.environ['NOTION_TOKEN']
    else:
        if not users[username].get('notion_api_token'):
            msg = bot.send_message(message.chat.id, 'please send me an Notion API key')
            bot.register_next_step_handler(msg, get_notion_api_token)
    #global notion_client
    #notion_client = NotionClient(token_v2=NOTION_TOKEN)
    users[username]['notion_client'] = NotionClient(token_v2=users[username]['notion_api_token'])
    bot.send_message(message.chat.id, 'Notion Client set!', reply_markup=basic_keyboard)


@bot.message_handler(commands=['checkclient'])
def checkclient_handler(message):
    username = message.from_user.username
    if users[username].get('notion_client'):
        bot.send_message(message.chat.id, 'Notion Client OK.', reply_markup=basic_keyboard)
        return
    bot.send_message(message.chat.id, 'Notion Client not set.', reply_markup=basic_keyboard)    


@bot.message_handler(commands=['setpage'])
def setpage_handler(message):
    msg = bot.send_message(message.chat.id, 'please send me an address of a page from your Notion')
    bot.register_next_step_handler(msg, get_page_address)


@bot.message_handler(commands=['checkpage'])
def checkpage_handler(message):
    username = message.from_user.username
    try:
        page = get_page(message)
        users[username]['page_title'] = f'{page.icon}{page.title}'
        bot.send_message(message.chat.id, f'your page is set to: {users[username]["page_title"]} ({users[username]["page_address"]})', reply_markup=basic_keyboard)
    except Exception as e:
            bot.send_message(message.chat.id, f'Error while checking page: {e}', reply_markup=basic_keyboard)


def get_notion_api_token(message):
    try:
        if not message.text:
            raise Exception()
        users[message.from_user.username]['notion_api_token'] = message.text
    except Exception as e:
        bot.send_message(message.chat.id, 'couldnt set Notion API token!')


def get_page_address(message):
    try:
        users[message.from_user.username]["page_address"] = message.text
        bot.send_message(message.chat.id, f'page set to {users[message.from_user.username]["page_address"]}!')
    except Exception as e:
        bot.send_message(message.chat.id, 'coldnt set page!')


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    try:
        page = get_page(message)
        newblock = page.children.add_new(TextBlock, title=text)
        bot.send_message(message.chat.id, f'sent text to {page.icon}{page.title}!', reply_markup=basic_keyboard)      
    except Exception as e:
        bot.send_message(message.chat.id, f'Error while sending text to Notion: {e}', reply_markup=basic_keyboard)   



@bot.message_handler(content_types=['video', 'photo', 'sticker', 'voice', 'location'])
def not_text_handler(message):
    bot.send_message(message.chat.id, 'you can only send text (for now).', reply_markup=basic_keyboard)


def get_page(message):
    username = message.from_user.username
    notion_client = users[username].get('notion_client')
    page_address = users[username].get('page_address')

    if not notion_client:
        raise Exception('Notion Client not set!')
    if not page_address:
        raise Exception('Page address not set!')

    page = notion_client.get_block(page_address)

    return page


bot.polling(none_stop=True, timeout=100)




    


