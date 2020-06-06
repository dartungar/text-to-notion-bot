import logging
import os
import db
from helpers import start, help_msg,  done
from helpers import ask_notion_api_key, set_notion_api_key, setclient, check_client
from helpers import askpage, set_page_address, connect_to_page, check_page, send_text_to_notion
from helpers import TYPING_NOTION_API_KEY, TYPING_NOTION_PAGE_ADDRESS, keyboard
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


BOT_TOKEN = os.environ.get('BOT_TOKEN_NOTION')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # pp = PicklePersistence(filename='notionbot')
    logger.info(f'bot token: {BOT_TOKEN}')
    updater = Updater(BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    convhandler = ConversationHandler(
        entry_points=[
                    CommandHandler('start', start),
                    CommandHandler('setclient', ask_notion_api_key),
                    CommandHandler('setpage', askpage),
                    ],

        states={
            TYPING_NOTION_API_KEY: [MessageHandler(Filters.text, set_notion_api_key)],
            TYPING_NOTION_PAGE_ADDRESS: [MessageHandler(Filters.text, set_page_address)],
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

    check_page_handler = CommandHandler('check_page', check_page)
    dp.add_handler(check_page_handler)

    send_text_to_notion_handler = MessageHandler(Filters.text, send_text_to_notion)
    dp.add_handler(send_text_to_notion_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
