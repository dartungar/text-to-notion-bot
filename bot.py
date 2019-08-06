import telebot
from notion.client import NotionClient
from notion.block import TextBlock
from to_notion import append_text_to_notion_page

#tokens 
TOKEN = '979211903:AAHfUniyo_3F4s48alBSW4hwNZXj4_DhS24'
token_notion = 'b90dcc81fb8148fd258e3f38f114c71a0f0bbd819c8a951deae384eb0a1dbecdb6a97b653abaa9b27562e66cd0f56dec6c574a9aa5c4592329fd9e9faff5f6c367e677f9869a9718fd32621b63be'

#create bot
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'go', 'activate'])
def start_handler(message):
    bot.send_message(message.chat.id, 'hey there, what\'s up?')



@bot.message_handler(commands=['setpage'])
def start_handler(message):
    bot.send_message(message.chat.id, 'please send me an address of a page from your Notion')
    # TODO: получить адрес из текста
    bot.register_next_step_handler(message, get_page_address)
    
    bot.send_message(message.chat.id, 'page set to {page_address}!')

def get_page_address(message):
    global page_address 
    page_address = message.text

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    append_text_to_notion_page(token_notion, page_address, text)
    bot.send_message(message.chat.id, 'sent text to {page_address}!')

bot.polling(none_stop=True, timeout=300)