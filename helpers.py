from db import session, User, create_new_user, check_if_user_exists
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from notion.client import NotionClient
from notion.block import TextBlock

TYPING_NOTION_API_KEY, TYPING_NOTION_PAGE_ADDRESS = range(2)

keyboard = ReplyKeyboardMarkup([['/start', '/help', '/setclient'], 
                                ['/check_client', '/setpage', '/check_page']], 
                               True)


def start(update, context):
    username = update.message.from_user.username
    
    if not check_if_user_exists(session, username):
        create_new_user(session, username)

    reply_text = f'''Hey there, {username}!
    I\'m a deadpan simple bot for appending text to Notion page.
    Use /help to get the instructions. 
    '''
    update.message.reply_text(reply_text, reply_markup=keyboard)
    check_client(update, context)
    check_page(update, context)


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
    7. use /setclient command and pass token_v2 to this bot
    8. choose Notion page to which you want send text, copy its URL
    9. use /setpage and send URL to context.bot

    Now any text you send to bot (except for commands) will be appended to Notion page you chose!
    '''
    update.message.reply_text(reply_text, reply_markup=keyboard)


def ask_notion_api_key(update, context):
    update.message.reply_text('please send me an Notion API key', reply_markup=keyboard)
    return TYPING_NOTION_API_KEY


def set_notion_api_key(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    user.notion_api_key = update.message.text
    session.commit()
    update.message.reply_text('✔️ Notion API key set.', reply_markup=keyboard)
    setclient(update, context, user)
    return ConversationHandler.END


def setclient(update, context, user):
    update.message.reply_text('Setting Notion client...')
    update.message.reply_text(f'Your API key is: {user.notion_api_key}')
    context.user_data['notion_client'] = NotionClient(token_v2=user.notion_api_key)
    update.message.reply_text('✔️ Notion client set!', reply_markup=keyboard)
    return ConversationHandler.END


def check_client(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    if not user.notion_api_key:
        update.message.reply_text('❌ Notion API key not set.', reply_markup=keyboard)
        ask_notion_api_key(update, context)

    if not context.user_data.get('notion_client'):
        update.message.reply_text('❌ Notion client not set.', reply_markup=keyboard)
        setclient(update, context, user)

    if user.notion_api_key:
        update.message.reply_text('✔️ Notion API key set!', reply_markup=keyboard)

    if context.user_data.get('notion_client'):
        update.message.reply_text('✔️ Notion client set!', reply_markup=keyboard)

    return ConversationHandler.END
        

def askpage(update, context):
    update.message.reply_text('please send me a URL of a page from your Notion.so', reply_markup=keyboard)
    return TYPING_NOTION_PAGE_ADDRESS
    

def setpage(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    
    if not user.page_address:
        page_address = update.message.text
        user.page_address = page_address
        notion_client = context.user_data['notion_client']
        page = notion_client.get_block(page_address)
        context.user_data['page'] = page
        user.page_title = page.title
        if page.icon:
            user.page_title = page.icon + page.title
        session.commit()
    
    if user.page_address:
        notion_client = context.user_data['notion_client']
        page = notion_client.get_block(user.page_address)
        context.user_data['page'] = page
    
    update.message.reply_text(f'page set to {user.page_title}')
    # если это не сделать, он уйдет в бесконечное 'page set to'!
    return ConversationHandler.END


def check_page(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()

    if not user.page_address:
        update.message.reply_text('❌ Page address not set.', reply_markup=keyboard)
        askpage(update, context)

    if user.page_address:
        update.message.reply_text(f'Notion page address set to {user.page_title}.', reply_markup=keyboard)
        

    if not context.user_data.get('page'):
        update.message.reply_text('❌ Page not set.', reply_markup=keyboard)
        setpage(update, context)

    if context.user_data.get('page'):
        update.message.reply_text('✔️ Page set!', reply_markup=keyboard)
    
    return ConversationHandler.END


def send_text_to_notion(update, context):
    username = update.message.from_user.username
    user = session.query(User).filter(User.username == username).first()
    
    try:
        text = update.message.text
        page = context.user_data['page']
        newblock = page.children.add_new(TextBlock, title=text)
        update.message.reply_text(f'Sent text to {user.page_title}.', reply_markup=keyboard)
    except Exception as e:
        update.message.reply_text(f'❌ Error while sending text to Notion: {e}', reply_markup=keyboard)


def done(update, context):
    update.message.reply_text('ok then.')
    return ConversationHandler.END


