import os
import telebot
from notion.client import NotionClient
from notion.block import TextBlock
from to_notion import append_text_to_notion_page


#tokens 
BOT_TOKEN = os.environ['BOT_TOKEN']
NOTION_TOKEN = os.environ['NOTION_TOKEN']


#create bot
bot = telebot.TeleBot(BOT_TOKEN)


#globals TODO fix this shit
page_address = ''
notion_client = ''


@bot.message_handler(commands=['start', 'go', 'activate'])
def start_handler(message):
    bot.send_message(message.chat.id, 
        '''Hey there! 
        I\'m a deadpan simple bot for appending text to Notion page. 
        Set page address with /setpage. 
        Then just send me text you want to appear in said Notion page.''')


@bot.message_handler(commands=['setclient'])
def setclient_handler(message):
    if not NOTION_TOKEN:
        msg = bot.send_message(message.chat.id, 'please send me an address of a page from your Notion')
        bot.register_next_step_handler(msg, get_notion_api_token)
    notion_client = NotionClient(token_v2=NOTION_TOKEN)
    bot.send_message(message.chat.id, 'Notion Client set!')


@bot.message_handler(commands=['setpage'])
def setpage_handler(message):
    msg = bot.send_message(message.chat.id, 'please send me an address of a page from your Notion')
    # TODO: получить адрес из текста
    bot.register_next_step_handler(msg, get_page_address)
    bot.send_message(message.chat.id, f'page set to {page_address}!')


def get_notion_api_token(message):
    NOTION_TOKEN = message.text


def get_page_address(message):
    page_address = message.text


def append_text_to_notion_page(client, page_address, text):
    page = client.get_block(page_address)
    newblock = page.children.add_new(TextBlock, title=text)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    append_text_to_notion_page(notion_client, page_address, text)
    bot.send_message(message.chat.id, f'sent text to {page_address}!')



bot.polling(none_stop=True, timeout=0)