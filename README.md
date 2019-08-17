# text-to-notion-bot

A (really) simple Telegram bot for sending text into Notion, built with python-telegram-bot and notion.py.
Here's how it works:
1. Get your 'token_v2' from cookies while being on any of your Notion.so pages.
2. Use /setclient command and pass token_v2's value to bot.
3. Use /setpage command and pass URL of your Notion.so page to bot.
4. You're set! Any text you send to bot afterwards will be appended to said Notion.so page.