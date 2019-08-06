def append_text_to_notion_page(api_token, page_address, text):
    client = NotionClient(token_v2=api_token)
    page = client.get_block(page_address)
    newblock = page.children.add_new(TextBlock, title=text)
