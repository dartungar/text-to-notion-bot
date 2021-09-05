# text-to-notion-bot

Really simple self-hosted single-user telegram bot for sending text into Notion, using the official API.

1. Register telegram bot and get bot token by communicationg with https://t.me/botfather
2. Create Notion Integration and get API key (https://developers.notion.com/docs/getting-started#step-1-create-an-integration)
3. 'Share' any Notion page with your Notion Integration (https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration)
4. Set up environment variables:
   - BOT_TOKEN=your telegram bot token
   - TELEGRAM_USERNAME=your telegram username (will be used for authorization)
   - NOTION_API_KEY=Notion API key
   - NOTION_PAGE_URL=URL of the page you shared with the integration (bot will parse page ID from it)
5. Run the bot.
   - Text sent to the bot will be added to Notion page specified in environment variable as child page.
   - Title and content will be equal to the text sent.
   - Long titles (>50 characters) will be truncated automatically
