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

keyboard = ReplyKeyboardMarkup([['/start', '/help', '/setclient'], ['/check_notion_api_key', '/setpage', '/checkpage']], True)


def start(update, context):
    context.user_data['username'] = update.message.from_user.username
    reply_text = f'''Hey there, {context.user_data['username']}! 
    I\'m a deadpan simple bot for appending text to Notion page.
    Get your "Notion API key" (go to any page in your Notion.so and look for "token_v2" in cookies). 
    Set your Notion Client with /setclient.
    Set page address with /setpage. 
    Then just send me text you want to appear on Notion page you set.'''
    update.message.reply_text(reply_text, reply_markup=keyboard)


def help_msg(update, context):
    reply_text = f'''In order to send stuff to Notion, you need to get your 'internal API key' for Notion.

    This 'token_v2' can be found in cookies on notion.so.
    Here's how to get it.

    1. go to any of your notion.so pages in browser
    2. press F12 / open developer tools 
    3. go to Application (Chrome) / Storage (Firefox) → cookies
    4. select "www.notion.so"
    5. find a cookie with name 'token_v2'
    6. copy its value
    7. use /setclient command and pass token_v2 to this context.bot
    8. choose Notion page to which you want send text, copy its URL
    9. use /setpage and send URL to context.bot

    Now any text you send to bot (except for commands) will be appended to Notion page you chose!
    '''
    update.message.reply_text(reply_text, reply_markup=keyboard)


def get_notion_api_key(update, context):
    if context.user_data['username'] == 'dartungar':
        context.user_data['notion_api_token'] = os.environ['NOTION_TOKEN']
        # сомнительная фигня, но стоит попробовать
        context.user_data['notion_client'] = NotionClient(token_v2=context.user_data['notion_api_token'])
        update.message.reply_text('Notion API key set. Welcome back, master!', reply_markup=keyboard)
        #return None
    if not context.user_data.get('notion_api_token'):
        update.message.reply_text('please send me an Notion API key', reply_markup=keyboard)
        return TYPING_NOTION_API_KEY


def setclient(update, context):
    context.user_data['notion_api_token'] = update.message.text
    # TODO это вообще работает? :D
    context.user_data['notion_client'] = NotionClient(token_v2=context.user_data['notion_api_token'])
    update.message.reply_text('Notion API key set!', reply_markup=keyboard)
    return ConversationHandler.END


def check_notion_api_key(update, context):
    if not context.user_data.get('notion_api_token'):
        update.message.reply_text('Notion API key not set! Please send me an Notion API key', reply_markup=keyboard)
        return TYPING_NOTION_API_KEY
    update.message.reply_text('Notion API key OK.', reply_markup=keyboard)    


def askpage(update, context):
    if not context.user_data.get('page_address'):
        update.message.reply_text('please send me a URL of a page from your Notion.so', reply_markup=keyboard)
        return TYPING_NOTION_PAGE_ADDRESS
    update.message.reply_text(f'Notion page address already set to {context.user_data["page_title"]}.', reply_markup=keyboard)
    return ConversationHandler.END

def setpage(update, context):
    if not context.user_data.get('page_address'):
        page_address = update.message.text
        context.user_data['page_address'] = page_address
        notion_client = context.user_data['notion_client']
        #notion_client = NotionClient(token_v2=context.user_data['notion_api_token'])
        page = notion_client.get_block(page_address)
        # тоже сомнительная фигня. или можно?
        context.user_data['page'] = page
        context.user_data['page_title'] = page.title
        if page.icon:
            context.user_data['page_title'] = page.icon + page.title
    
    update.message.reply_text(f'page set to {context.user_data["page_title"]}')
    # если это не сделать, он уйдет в бесконечное 'page set to'!
    return ConversationHandler.END
    


def checkpage(update, context):
    if not context.user_data.get('page_address'):
        update.message.reply_text('Notion page address not set!', reply_markup=keyboard)
        return ConversationHandler.END
    update.message.reply_text('Notion page address set.', reply_markup=keyboard)


def send_text_to_notion(update, context):
    try:
        text = update.message.text
        #notion_client = NotionClient(token_v2=context.user_data['notion_api_token'])
        #page = notion_client.get_block(context.user_data['page_address'])
        notion_client = context.user_data['notion_client']
        page = context.user_data['page']
        newblock = page.children.add_new(TextBlock, title=text)
        update.message.reply_text(f'Sent text to {context.user_data["page_title"]}.', reply_markup=keyboard)
    except Exception as e:
        update.message.reply_text(f'Error while sending text to Notion: {e}', reply_markup=keyboard)


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
                        CommandHandler('setclient', get_notion_api_key), 
                        CommandHandler('setpage', askpage),],

        states={
            TYPING_NOTION_API_KEY: [MessageHandler(Filters.text, setclient)],
            TYPING_NOTION_PAGE_ADDRESS: [MessageHandler(Filters.text, setpage)],  
        },

        fallbacks=[CommandHandler('done', done)],
        name='my_conversation',
        persistent=True
    )

    dp.add_handler(convhandler)

    help_handler = CommandHandler('help', help_msg)
    dp.add_handler(help_handler)

    check_notion_api_key_handler = CommandHandler('check_notion_api_key', check_notion_api_key)
    dp.add_handler(check_notion_api_key_handler)

    checkpage_handler = CommandHandler('checkpage', checkpage)
    dp.add_handler(checkpage_handler)

    send_text_to_notion_handler = MessageHandler(Filters.text, send_text_to_notion)
    dp.add_handler(send_text_to_notion_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()