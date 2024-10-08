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

    def all_users(self):
        return self.users.all()

    @cached(ttl=5 * 60, noself=True)
    async def async_all_users(self):
        result, timeouted = await self.executor.run(self.all_users)
        if timeouted:
            raise TimeoutError()
        return result

    def upsert_user(self, user: User):
        user_row = {
            "fields": {
                "TelegramID": user.id,
                "Name": user.full_name,
                "Username": user.username,
                "LanguageCode": user.language_code,
            }
        }

        records = self.users.batch_upsert([user_row], key_fields=["TelegramID"])

        return records[0]["id"]

    def _create_row(
        self,
        text,
        attachment_type,
        attachment_url,
        attachment_filename,
        attachment_file_id,
        author_record_id,
        suggestor_record_id=None,
    ):
        row = {
            "Text": text,
            "AttachmentType": attachment_type,
            "AttachmentFileID": attachment_file_id,
            "Author": [author_record_id],
        }
        if attachment_url:
            row["Attachment"] = [
                {"url": attachment_url, "filename": attachment_filename}
            ]
        if suggestor_record_id:
            row["Suggestor"] = [suggestor_record_id]
        return row

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
        author_record_id = self.upsert_user(author)
        suggestor_record_id = self.upsert_user(suggestor)
        row = self._create_row(
            text,
            attachment_type,
            attachment_url,
            attachment_filename,
            attachment_file_id,
            author_record_id,
            suggestor_record_id,
        )
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
        author_record_id = self.upsert_user(author)
        row = self._create_row(
            text,
            attachment_type,
            attachment_url,
            attachment_filename,
            attachment_file_id,
            author_record_id,
        )
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

    def update_file_id(
        self,
        kek_id: str,
        attachment_file_id: str,
    ):
        return self.list.update(kek_id, {"AttachmentFileID": attachment_file_id})

    async def async_update_file_id(
        self,
        kek_id: str,
        attachment_file_id: str,
    ):
        result, timeouted = await self.executor.run(
            self.update_file_id, kek_id, attachment_file_id
        )
        if timeouted:
            raise TimeoutError()
        return result


kek_storage = KekStorage()
