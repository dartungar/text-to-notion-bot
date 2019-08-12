import os
import telebot
from notion.client import NotionClient
from notion.block import TextBlock

#tokens TODO delete Notion Noket from here
BOT_TOKEN = os.environ['BOT_TOKEN']
NOTION_TOKEN = None #os.environ['NOTION_TOKEN']


#create bot
bot = telebot.TeleBot(BOT_TOKEN)

#lame disct for storing users
users = {}

#globals TODO fix this shit (with user dictionary?)
page_address = None
notion_client = None

basic_keyboard = telebot.types.ReplyKeyboardMarkup(True)
btn1 = telebot.types.KeyboardButton('/start')
btn2 = telebot.types.KeyboardButton('/setclient')
btn3 = telebot.types.KeyboardButton('/setpage')
btn4 = telebot.types.KeyboardButton('/checkpage')
basic_keyboard.add(btn1, btn2, btn3, btn4)


# TODO: более элегантное решение с диктами
@bot.message_handler(commands=['start', 'go', 'activate'])
def start_handler(message):
        username = message.from_user.username
        users[username] = username
        users[username]['name'] = username
        bot.send_message(message.chat.id, 
        f'''Hey there, {username}! 
        I\'m a deadpan simple bot for appending text to Notion page. 
        Set your Notion Client with /setclient.
        Set page address with /setpage. 
        Then just send me text you want to appear in said Notion page.''', 
        reply_markup=basic_keyboard)



@bot.message_handler(commands=['setclient'])
def setclient_handler(message):
        if message.from_user.username == 'dartungar':
                NOTION_TOKEN = os.environ['NOTION_TOKEN']
        if not NOTION_TOKEN:
                msg = bot.send_message(message.chat.id, 'please send me an Notion API key')
                bot.register_next_step_handler(msg, get_notion_api_token)
        global notion_client
        notion_client = NotionClient(token_v2=NOTION_TOKEN)
        bot.send_message(message.chat.id, 'Notion Client set!', reply_markup=basic_keyboard)


@bot.message_handler(commands=['setpage'])
def setpage_handler(message):
    msg = bot.send_message(message.chat.id, 'please send me an address of a page from your Notion')
    bot.register_next_step_handler(msg, get_page_address)


@bot.message_handler(commands=['checkpage'])
def checkpage_handler(message):
        try:
                page_title = notion_client.get_block(page_address).title
                page_icon = notion_client.get_block(page_address).icon
                bot.send_message(message.chat.id, f'your page is set to: {page_icon}{page_title} ({page_address})', reply_markup=basic_keyboard)
        except Exception as e:
                bot.send_message(message.chat.id, f'Error while checking page: {e}!', reply_markup=basic_keyboard)


def get_notion_api_token(message):
    try:
        global NOTION_TOKEN
        if not message.text:
                raise Exception()
        NOTION_TOKEN = message.text
    except Exception as e:
        bot.send_message(message.chat.id, 'couldnt get Notion API!')


def get_page_address(message):
    try:
        global page_address
        page_address = message.text
        bot.send_message(message.chat.id, f'page set to {page_address}!')
    except Exception as e:
        bot.send_message(message.chat.id, 'coldnt set page!')


@bot.message_handler(content_types=['text'])
def text_handler(message):
        text = message.text
        try:
                if not notion_client:
                        raise Exception('Notion Client not set!')
                page = notion_client.get_block(page_address)
                newblock = page.children.add_new(TextBlock, title=text)
                bot.send_message(message.chat.id, f'sent text to {page.title}!', reply_markup=basic_keyboard)      
        except Exception as e:
                bot.send_message(message.chat.id, f'Error while sending text to Notion: {e}!', reply_markup=basic_keyboard)   





@bot.message_handler(content_types=['video', 'photo', 'sticker', 'voice', 'location'])
def not_text_handler(message):
    bot.send_message(message.chat.id, 'you can only send text (for now).', reply_markup=basic_keyboard)


bot.polling(none_stop=True, timeout=100)

