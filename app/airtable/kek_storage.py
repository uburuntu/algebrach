from aiocache import cached
from aiogram.types import User
from common.executor import ThreadPoolExecutor
from pyairtable import Api, retry_strategy
from settings import config


class KekStorage:
    """
    Kek Storage connected to Airtable base

    https://airtable.com/appG5koP3D8kWbLdl/
    """

    def __init__(self):
        self.api = Api(
            config.airtable_access_token,
            timeout=(3, 5),
            retry_strategy=retry_strategy(total=2),
        )

        self.base = self.api.get_base(config.airtable_base_id)

        self.list = self.base.get_table("List")
        self.users = self.base.get_table("Users")
        self.suggestions = self.base.get_table("Suggestions")

        self.executor = ThreadPoolExecutor(max_workers=1)

    def all(self):
        return self.list.all()

    @cached(ttl=5 * 60, noself=True)
    async def async_all(self):
        result, timeouted = await self.executor.run(self.all)
        if timeouted:
            raise TimeoutError()
        return result

    def add(
        self,
        author: User,
        suggestor: User,
        text: str | None,
        attachment_url: str | None,
        attachment_type: str | None,
        attachment_filename: str | None,
        attachment_file_id: str | None,
    ):
        author_row, suggestor_row = (
            {
                "fields": {
                    "TelegramID": u.id,
                    "Name": u.full_name,
                    "Username": u.username,
                    "LanguageCode": u.language_code,
                }
            }
            for u in (author, suggestor)
        )

        records = self.users.batch_upsert([author_row], key_fields=["TelegramID"])
        author_record_id = records[0]["id"]

        records = self.users.batch_upsert([suggestor_row], key_fields=["TelegramID"])
        suggestor_record_id = records[0]["id"]

        row = {
            "Text": text,
            "AttachmentType": attachment_type,
            "Attachment": (
                [{"url": attachment_url, "filename": attachment_filename}]
                if attachment_url
                else None
            ),
            "AttachmentFileID": attachment_file_id,
            "Author": [author_record_id],
            "Suggestor": [suggestor_record_id],
        }
        return self.suggestions.create(row)

    async def async_add(
        self,
        author: User,
        suggestor: User,
        text: str | None,
        attachment_url: str | None,
        attachment_type: str | None,
        attachment_filename: str | None,
        attachment_file_id: str | None,
    ):
        result, timeouted = await self.executor.run(
            self.add,
            author,
            suggestor,
            text,
            attachment_url,
            attachment_type,
            attachment_filename,
            attachment_file_id,
        )
        if timeouted:
            raise TimeoutError()
        return result

    def push(
        self,
        author: User,
        text: str | None,
        attachment_url: str | None,
        attachment_type: str | None,
        attachment_filename: str | None,
        attachment_file_id: str | None,
    ):
        (author_row,) = (
            {
                "fields": {
                    "TelegramID": u.id,
                    "Name": u.full_name,
                    "Username": u.username,
                    "LanguageCode": u.language_code,
                }
            }
            for u in (author,)
        )

        records = self.users.batch_upsert([author_row], key_fields=["TelegramID"])
        author_record_id = records[0]["id"]

        row = {
            "Text": text,
            "AttachmentType": attachment_type,
            "Attachment": (
                [{"url": attachment_url, "filename": attachment_filename}]
                if attachment_url
                else None
            ),
            "AttachmentFileID": attachment_file_id,
            "Author": [author_record_id],
        }
        return self.list.create(row)

    async def async_push(
        self,
        author: User,
        text: str | None,
        attachment_url: str | None,
        attachment_type: str | None,
        attachment_filename: str | None,
        attachment_file_id: str | None,
    ):
        result, timeouted = await self.executor.run(
            self.push,
            author,
            text,
            attachment_url,
            attachment_type,
            attachment_filename,
            attachment_file_id,
        )
        if timeouted:
            raise TimeoutError()
        return result


kek_storage = KekStorage()
