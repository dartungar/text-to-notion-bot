import os
import requests
import re
import json


class NotionService:
    BASE_API_URL = 'https://api.notion.com/v1/pages'

    PAGE_TITLE_MAX_LENGTH = 40

    def __init__(self) -> None:
        pass

    def setup_settings(self) -> None:
        self.api_key: str = os.getenv('NOTION_API_KEY')
        self.page_url: str = os.getenv('NOTION_PAGE_URL')
        self.page_id: str = self.get_page_id_from_url(self.page_url)
        self.URL_HEADERS = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }

    def create_page(self, text: str) -> None:
        headers = self.URL_HEADERS

        payload = self.generate_create_page_request_body(text)
        response = requests.post(
            self.BASE_API_URL, headers=headers, data=json.dumps(payload))

        if not response.ok:
            raise NotionServiceException(response.json())

    def generate_create_page_request_body(self, text) -> object:
        title = text if len(
            text) < self.PAGE_TITLE_MAX_LENGTH else text[:self.PAGE_TITLE_MAX_LENGTH]+'...'
        return {
            "parent": {
                "page_id": self.page_id
            },
            "properties": {
                "title": {"title": [{"type": "text", "text": {"content": title}}]},

            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"type": "text", "text": {"content": text}}]
                    }
                }
            ]
        }

    def get_page_id_from_url(self, url: str) -> str:
        id_regex = re.compile(r'([\w|\d]{32}$)')
        id_raw = id_regex.findall(url)[0]
        id_processed = '-'.join([
            id_raw[0:8], id_raw[8:12], id_raw[12:16], id_raw[16:20], id_raw[20:]])
        return id_processed


class NotionServiceException(Exception):
    pass
