from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.future import select
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    CONTAINER_PREFIX: Optional[str] = None
    KT_CLOUD_API_KEY: Optional[str] = None
    KT_CLOUD_SECRET_KEY: Optional[str] = None
    KT_CLOUD_RESELLER_KEY: Optional[str] = None
    NAVER_CLOUD_API_KEY: Optional[str] = None
    NAVER_CLOUD_SECRET_KEY: Optional[str] = None
    NAVER_CLOUD_GOV_API_KEY: Optional[str] = None
    NAVER_CLOUD_GOV_SECRET_KEY: Optional[str] = None
    NHN_CLOUD_API_KEY: Optional[str] = None
    NHN_CLOUD_SECRET_KEY: Optional[str] = None
    NHN_CLOUD_ACCESS_TOKEN: Optional[str] = None
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[str] = None
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DATABASE: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

Base = declarative_base()

class AsyncDatabase:
    def __init__(self, model):
        DB_URL = (
            f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8"
        )

        engine = create_async_engine(DB_URL, echo=True)
        self.SessionLocal = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        self.model = model

    async def get_all(self):
        async with self.SessionLocal() as session:
            result = await session.execute(select(self.model))
            result_list = result.scalars().all()
            output_list = []
            for result_element in result_list:
                output_list.append({c.name: getattr(result_element, c.name) for c in result_element.__table__.columns})
            return output_list

    async def get(self, id):
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar()

    async def save(self, document):
        async with self.SessionLocal() as session:
            session.add(document)
            await session.commit()

    async def update_one(self, id_field_name, id_value, dic):
        async with self.SessionLocal() as session:
            model_class = self.model
            id_field = getattr(model_class, id_field_name)
            
            result = await session.execute(
                select(model_class).where(id_field == id_value)
            )
            
            doc = result.scalar()
            if doc:
                for key, value in dic.items():
                    setattr(doc, key, value)
                await session.commit()
                return True
            return False

    async def delete_one(self, id):
        async with self.SessionLocal() as session:
            result = await session.execute(
                select(self.model).where(self.model.id == id)
            )
            doc = result.scalar()
            if doc:
                await session.delete(doc)
                await session.commit()
                return True
            return False

    async def gets_by_conditions(self, conditions):
        async with self.SessionLocal() as session:
            result = await session.execute(select(self.model).filter_by(**conditions))
            result_list = result.scalars().all()
            output_list = []
            for result_element in result_list:
                output_list.append({c.name: getattr(result_element, c.name) for c in result_element.__table__.columns})
            return output_list

    async def get_by_conditions(self, conditions):
        async with self.SessionLocal() as session:
            result = await session.execute(select(self.model).filter_by(**conditions))
            result_element = result.scalars().one()
            output = {c.name: getattr(result_element, c.name) for c in result_element.__table__.columns}
            return output
