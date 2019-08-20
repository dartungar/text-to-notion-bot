import logging
import os
import db
from db import session, User, create_new_user, check_if_user_exists
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler, ConversationHandler, Filters, PicklePersistence
from notion.client import NotionClient
from notion.block import TextBlock
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


BOT_TOKEN = os.environ.get('BOT_TOKEN')


TYPING_NOTION_API_KEY, TYPING_NOTION_PAGE_ADDRESS = range(2)

keyboard = ReplyKeyboardMarkup([['/start', '/help', '/setclient'], ['/check_client', '/setpage', '/checkpage']], True)


def start(update, context):
    username = update.message.from_user.username
    if not check_if_user_exists(session, username):
        create_new_user(session, username)
    reply_text = f'''Hey there, {username}!
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
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    if not user.notion_api_key:
        update.message.reply_text('please send me an Notion API key', reply_markup=keyboard)
        return TYPING_NOTION_API_KEY
    
    update.message.reply_text('Notion API key already set. Welcome back!', reply_markup=keyboard)
    setclient(update, context, user)
    return ConversationHandler.END


def set_notion_api_key(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    user.notion_api_key = update.message.text
    session.commit()
    update.message.reply_text('Notion API key set.', reply_markup=keyboard)
    setclient(update, context, user)
    return ConversationHandler.END


def setclient(update, context, user): 
    
    context.user_data['notion_client'] = NotionClient(token_v2=user.notion_api_key)
    update.message.reply_text('Notion client set!', reply_markup=keyboard)
    #return ConversationHandler.END


def check_client(update, context):
    if not context.user_data.get('notion_api_token'):
        update.message.reply_text('Notion API key not set! Please send me an Notion API key', reply_markup=keyboard)
        return TYPING_NOTION_API_KEY
    update.message.reply_text('Notion API key OK.', reply_markup=keyboard)
    if not context.user_data['notion_client']:
        username = update.message.from_user.username
        user = session.query(User).filter(User.username == username).first()
        setclient(update, context, user)
        return ConversationHandler.END


def askpage(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    if not user.page_address:
        update.message.reply_text('please send me a URL of a page from your Notion.so', reply_markup=keyboard)
        return TYPING_NOTION_PAGE_ADDRESS
    if user.page_address:
        update.message.reply_text(f'Notion page address already set to {user.page_title}.', reply_markup=keyboard)
        return ConversationHandler.END


def setpage(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    if not user.page_address:
        page_address = update.message.text
        user.page_address = page_address
        notion_client = context.user_data['notion_client']
        #notion_client = NotionClient(token_v2=context.user_data['notion_api_token'])
        page = notion_client.get_block(page_address)
        # тоже сомнительная фигня. или можно?
        context.user_data['page'] = page
        user.page_title = page.title
        if page.icon:
            user.page_title = page.icon + page.title
        session.commit()
    
    update.message.reply_text(f'page set to {user.page_title}')
    # если это не сделать, он уйдет в бесконечное 'page set to'!
    return ConversationHandler.END
    


def checkpage(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    if not user.page_address:
        update.message.reply_text('Notion page address not set!', reply_markup=keyboard)
        askpage(update, context)
    update.message.reply_text('Notion page address set.', reply_markup=keyboard)
    return ConversationHandler.END


def send_text_to_notion(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    try:
        text = update.message.text
        #notion_client = NotionClient(token_v2=context.user_data['notion_api_token'])
        #page = notion_client.get_block(context.user_data['page_address'])
        notion_client = context.user_data['notion_client']
        page = context.user_data['page']
        newblock = page.children.add_new(TextBlock, title=text)
        update.message.reply_text(f'Sent text to {user.page_title}.', reply_markup=keyboard)
    except Exception as e:
        update.message.reply_text(f'Error while sending text to Notion: {e}', reply_markup=keyboard)


def done(update, context):
    update.message.reply_text('ok then.')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)



def main():
    #pp = PicklePersistence(filename='notionbot')
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    convhandler = ConversationHandler(
        entry_points=[
                    CommandHandler('start', start), 
                    CommandHandler('setclient', get_notion_api_key), 
                    CommandHandler('setpage', askpage),
                    ],

        states={
            TYPING_NOTION_API_KEY: [MessageHandler(Filters.text, set_notion_api_key)],
            TYPING_NOTION_PAGE_ADDRESS: [MessageHandler(Filters.text, setpage)],  
        },

        fallbacks=[CommandHandler('done', done)],
        name='my_conversation',
        persistent=False
    )

    dp.add_handler(convhandler)

    help_handler = CommandHandler('help', help_msg)
    dp.add_handler(help_handler)

    check_client_handler = CommandHandler('check_client', check_client)
    dp.add_handler(check_client_handler)

    checkpage_handler = CommandHandler('checkpage', checkpage)
    dp.add_handler(checkpage_handler)

    send_text_to_notion_handler = MessageHandler(Filters.text, send_text_to_notion)
    dp.add_handler(send_text_to_notion_handler)

    dp.add_error_handler(error)







    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()