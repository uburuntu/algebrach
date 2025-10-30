from aiocache import cached
from aiogram.types import User
from common.executor import ThreadPoolExecutor
from models import KekRecord, UserRecord
from pyairtable import Api, retry_strategy
from settings import config
from tenacity import retry, stop_after_attempt, wait_exponential


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
        """Fetch all kek records from Airtable."""
        raw_records = self.list.all()
        # Validate and parse records using Pydantic models
        return [KekRecord(**record).model_dump() for record in raw_records]

    @cached(ttl=config.kek_cache_ttl_seconds, noself=True)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def async_all(self):
        """Async wrapper to fetch all keks with retry logic."""
        result, timeouted = await self.executor.run(self.all)
        if timeouted:
            raise TimeoutError("Airtable query timed out")
        return result

    def all_users(self):
        """Fetch all user records from Airtable."""
        raw_records = self.users.all()
        # Validate and parse records using Pydantic models
        return [UserRecord(**record).model_dump() for record in raw_records]

    @cached(ttl=config.kek_cache_ttl_seconds, noself=True)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def async_all_users(self):
        """Async wrapper to fetch all users with retry logic."""
        result, timeouted = await self.executor.run(self.all_users)
        if timeouted:
            raise TimeoutError("Airtable query timed out")
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
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
        """Async wrapper to add a kek suggestion with retry logic."""
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
            raise TimeoutError("Airtable add operation timed out")
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def async_push(
        self,
        author: User,
        text: str | None,
        attachment_url: str | None,
        attachment_type: str | None,
        attachment_filename: str | None,
        attachment_file_id: str | None,
    ):
        """Async wrapper to push a kek directly to the list with retry logic."""
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
            raise TimeoutError("Airtable push operation timed out")
        return result

    def update_file_id(
        self,
        kek_id: str,
        attachment_file_id: str,
    ):
        return self.list.update(kek_id, {"AttachmentFileID": attachment_file_id})

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def async_update_file_id(
        self,
        kek_id: str,
        attachment_file_id: str,
    ):
        """Async wrapper to update file ID with retry logic."""
        result, timeouted = await self.executor.run(
            self.update_file_id, kek_id, attachment_file_id
        )
        if timeouted:
            raise TimeoutError("Airtable update operation timed out")
        return result


kek_storage = KekStorage()
