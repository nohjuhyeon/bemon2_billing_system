from typing import Any, List, Optional
from beanie import init_beanie, PydanticObjectId
from models.user_list import User_list
from models.total_charge import Total_charge
from models.cloud_list import Cloud_list
from models.service_charge_list import Service_charge_list
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
import numpy


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    CONTAINER_PREFIX: Optional[str] = None
    kt_cloud_api_key: Optional[str] = None
    kt_cloud_secret_key: Optional[str] = None
    kt_cloud_reseller_key: Optional[str] = None
    naver_cloud_api_key: Optional[str] = None
    naver_cloud_secret_key: Optional[str] = None
    naver_cloud_gov_api_key: Optional[str] = None
    naver_cloud_gov_secret_key: Optional[str] = None
    nhn_cloud_api_key: Optional[str] = None
    nhn_cloud_secret_key: Optional[str] = None
    nhn_cloud_access_token: Optional[str] = None

    async def initialize_database(self):
        client = AsyncIOMotorClient(self.DATABASE_URL)
        await init_beanie(
            database=client.get_default_database(),
            document_models=[User_list, Total_charge,Cloud_list,Service_charge_list],
        )

    class Config:
        env_file = ".env"


class Database:
    # model 즉 collection
    def __init__(self, model) -> None:
        self.model = model
        pass

    # 전체 리스트
    async def get_all(self):
        documents = await self.model.find_all().to_list()
        pass
        return documents

    # 상세 보기
    async def get(self, id: PydanticObjectId) -> Any:
        doc = await self.model.get(id)
        if doc:
            return doc
        return False

    # 저장
    async def save(self, document) -> None:
        await document.create()
        return None

    # 업데이트
    async def update_one(self, id: PydanticObjectId, dic) -> Any:
        doc = await self.model.get(id)
        if doc:
            for key, value in dic.items():
                setattr(doc, key, value)
            await doc.save()
            return True
        return False

    # 삭제
    async def delete_one(self, id: PydanticObjectId) -> bool:
        doc = await self.model.get(id)
        if doc:
            await doc.delete()
            return True
        return False

    async def getsbyconditions(self, conditions: dict) -> [Any]:
        documents = await self.model.find(conditions).to_list()  # find({})
        if documents:
            return documents
        return False

    async def getsbyconditionswithpagination(
        self, conditions: dict, page_number, records_per_page=10
    ) -> [Any]:
        # find({})
        total = await self.model.find(conditions).count()
        pagination = Paginations(
            total_records=total,
            current_page=page_number,
            records_per_page=records_per_page,
        )
        documents = (
            await self.model.find(conditions)
            .skip(pagination.start_record_number - 1)
            .limit(pagination.records_per_page)
            .to_list()
        )
        if documents:
            return documents, pagination
        return pagination
