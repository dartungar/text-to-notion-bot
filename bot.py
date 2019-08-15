import logging
import os
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters, PicklePersistence
from notion.client import NotionClient
from notion.block import TextBlock

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    BOT_TOKEN = '979211903:AAHfUniyo_3F4s48alBSW4hwNZXj4_DhS24'

TYPING_NOTION_API_KEY, TYPING_NOTION_PAGE_ADDRESS = range(2)

keyboard = ReplyKeyboardMarkup([['/start', '/help', '/setclient'], ['/checkclient', '/setpage', '/checkpage']], True)


def start(update, context):
    context.user_data['username'] = update.message.from_user.username
    reply_text = f'''Hey there, {context.user_data['username']}! 
    I\'m a deadpan simple context.bot for appending text to Notion page.
    Get your "Notion API key" (go to any page in your Notion.so and look for "token_v2" in cookies). 
    Set your Notion Client with /setclient.
    Set page address with /setpage. 
    Then just send me text you want to appear on Notion page you set.'''
    update.message.reply_text(reply_text, reply_markup=keyboard)


def help_msg(update, context):
    reply_text = f'''In order to send stuff to Notion, you need to get your 'internal API key' for Notion.

    1. go to any of your notion.so pages in browser
    2. press F12 / open developer tools 
    3. go to Application (Chrome) / Storage (Firefox) → cookies
    4. select https://www.notion.so
    5. find a cookie with name 'token_v2'
    6. copy its value
    7. use /setclient command and pass token_v2 to this context.bot
    8. choose Notion page to which you want send text, copy its URL
    9. use /setpage and send URL to context.bot

    Now any text you send to bot (except for commands) will be appended to Notion page you chose!
    '''
    update.message.reply_text(reply_text, reply_markup=keyboard)


def askclient(update, context):
    if context.user_data['username'] == 'dartungar':
        context.user_data['notion_api_token'] = os.environ['NOTION_TOKEN']
        update.message.reply_text('welcome back, master Dartio!', reply_markup=keyboard)
        return
    if not context.user_data.get('notion_api_token'):
        update.message.reply_text('please send me an Notion API key', reply_markup=keyboard)
        return TYPING_NOTION_API_KEY


def setclient(update, context):
    context.user_data['notion_api_token'] = update.message.text
    # TODO это вообще работает? :D
    context.user_data['notion_client'] = NotionClient(token_v2=context.user_data['notion_api_token'])
    update.message.reply_text('Notion Client set!', reply_markup=keyboard)


def askpage(update, context):
    if not context.user_data.get('page_address'):
        update.message.reply_text('please send me a URL of a page from your Notion.so', reply_markup=keyboard)
        return TYPING_NOTION_PAGE_ADDRESS


def setpage(update, context):
    page_address = update.message.text
    context.user_data['page_address'] = page_address
    notion_client = context.user_data['notion_client']
    page = notion_client.get_block(page_address)
    context.user_data['page'] = page
    if page.icon:
        context.user_data['page_title'] += page.icon
    context.user_data['page_title'] += page.title
    # TODO message from bot 
    

def send_text_to_notion(update, context):
    text = update.message.text
    page = context.user_data['page']
    newblock = page.children.add_new(TextBlock, title=text)


def done(update, context):
    update.message.reply_text('ok then.')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)




def main():
    pp = PicklePersistence(filename='notionbot')
    updater = Updater(BOT_TOKEN, persistence=pp, use_context=True)

    dp = updater.dispatcher

    convhandler = ConversationHandler(
        entry_points=[CommandHandler('start', start), 
                        CommandHandler('setclient', askclient), 
                        CommandHandler('setpage', askpage),],

        states={
            TYPING_NOTION_API_KEY: [MessageHandler(Filters.text, setclient)],
            TYPING_NOTION_PAGE_ADDRESS: [MessageHandler(Filters.text, setpage)],  
        },

        fallbacks=[RegexHandler('^Done$', done)],
        name='my_conversation',
        persistent=True

    )

    dp.add_handler(convhandler)
    help_handler = CommandHandler('help', help_msg)
    dp.add_handler(help_handler)
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()




if __name__ == '__main__':
    main()