import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters
from NotionService import NotionService
from typing import Type

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        self.setup()
        self.updater.start_polling()
        self.updater.idle()

    def setup(self) -> None:
        try:
            self.BOT_TOKEN: str = os.getenv('BOT_TOKEN')
            self.USERNAME: str = os.getenv('TELEGRAM_USERNAME')
            self.notion: NotionService = NotionService()
            self.updater: Type[Updater] = Updater(
                self.BOT_TOKEN, use_context=True)
            self.dispatcher = self.updater.dispatcher
            self.notion.setup_settings()
            self.register_handlers()
        except Exception as e:
            raise BotException(e)

    def register_handlers(self) -> None:
        self.dispatcher.add_handler(self.text_handler())
        self.dispatcher.add_handler(self.start_handler())
        self.dispatcher.add_handler(self.help_handler())
        self.dispatcher.add_error_handler(self.error)

    def text_handler(self) -> Type[MessageHandler]:
        return MessageHandler(Filters.text, self.send_to_notion)

    def send_to_notion(self, update, context):
        sender_username = update.message.from_user.username
        if sender_username == self.USERNAME:
            self.notion.create_page(update.message.text)
            logger.info('Successfully sent message to Notion')
            update.message.reply_text("Text sent to Notion.")
        else:
            update.message.reply_text(
                "⛔ Sorry, you are not authorized for this bot.")

    def start_handler(self) -> Type[CommandHandler]:
        return CommandHandler('start', help)

    def help_handler(self) -> Type[CommandHandler]:
        return CommandHandler('help', help)

    def help(self, update, context):
        reply_text = '''
        1. Set up environment variables for BOT_TOKEN, USERNAME, NOTION_API_KEY, OTION_PAGE_URL https://github.com/dartungar/text-to-notion-bot
        2. Send text here
        3. Have a nice day!
        '''
        update.message.reply_text(reply_text)

    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


class BotException(Exception):
    pass
