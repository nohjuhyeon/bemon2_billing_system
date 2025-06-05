from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.future import select
from typing import Optional
from sqlalchemy import and_, or_

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

        # 수정된 엔진 생성
        engine = create_async_engine(
            DB_URL,
            echo=False,
            pool_pre_ping=True,  # 연결 상태를 미리 확인
            pool_recycle=3600,   # 연결 재활용 시간 (1시간)
            pool_size=10,        # 연결 풀 최대 크기
            max_overflow=5       # 추가 연결 허용 수
        )

        # 수정된 세션 생성
        self.SessionLocal = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

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

    async def delete_one(self, id_field_name,id_value):
        async with self.SessionLocal() as session:
            model_class = self.model
            id_field = getattr(model_class, id_field_name)
            result = await session.execute(
                select(self.model).where(id_field == id_value)
            )
            doc = result.scalar()
            if doc:
                await session.delete(doc)
                await session.commit()
                return True
            return False
    async def delete_many(self, field_name, values):
        """
        Deletes multiple records based on the provided field and values.

        Args:
            field_name (str): The name of the field to filter records.
            values (list or single value): A list of values or a single value to match for deletion.

        Returns:
            int: The number of records deleted.
        """
        # Ensure `values` is a list (even for a single value)
        if not isinstance(values, (list, tuple)):
            values = [values]

        # Return immediately if `values` is empty
        if not values:
            return 0

        async with self.SessionLocal() as session:
            model_class = self.model
            field = getattr(model_class, field_name)
            
            # Fetch all records matching the condition
            result = await session.execute(
                select(model_class).where(field.in_(values))
            )
            docs = result.scalars().all()
            
            if docs:
                for doc in docs:
                    await session.delete(doc)
                await session.commit()
                return len(docs)  # Return the count of deleted records
            
            return 0  # No records deleted

    async def gets_by_conditions(self, conditions):
        async with self.SessionLocal() as session:
            # 조건 생성
            filters = []
            for key, value in conditions.items():
                column = getattr(self.model, key)
                if isinstance(value, dict):  # 값이 딕셔너리인 경우 (비교 연산자 처리)
                    if "eq" in value:  # 동등 비교
                        filters.append(column == value["eq"])
                    if "like" in value:  # 문자열 포함 여부 (LIKE)
                        filters.append(column.like(f"%{value['like']}%"))
                    if "gte" in value:  # 크거나 같음
                        filters.append(column >= value["gte"])
                    if "lte" in value:  # 작거나 같음
                        filters.append(column <= value["lte"])
                    if "gt" in value:  # 큼
                        filters.append(column > value["gt"])
                    if "lt" in value:  # 작음
                        filters.append(column < value["lt"])
                    if "in" in value:  # 리스트 포함 여부
                        filters.append(column.in_(value["in"]))
                    if "not_in" in value:  # 리스트에 포함되지 않는 경우
                        filters.append(~column.in_(value["not_in"]))
                else:  # 단순 동등 비교
                    filters.append(column == value)

            # 필터를 and_로 묶음
            final_filter = and_(*filters)

            # 쿼리 실행
            result = await session.execute(select(self.model).filter(final_filter))
            result_list = result.scalars().all()

            # 결과 변환
            output_list = []
            for result_element in result_list:
                output_list.append({c.name: getattr(result_element, c.name) for c in result_element.__table__.columns})
            return output_list


    async def get_by_conditions(self, conditions):
        async with self.SessionLocal() as session:
            # 조건 생성
            filters = []
            for key, value in conditions.items():
                column = getattr(self.model, key)
                if isinstance(value, dict):  # 값이 딕셔너리인 경우 (비교 연산자 처리)
                    if "eq" in value:  # 동등 비교
                        filters.append(column == value["eq"])
                    if "like" in value:  # 문자열 포함 여부 (LIKE)
                        filters.append(column.like(f"%{value['like']}%"))
                    if "gte" in value:  # 크거나 같음
                        filters.append(column >= value["gte"])
                    if "lte" in value:  # 작거나 같음
                        filters.append(column <= value["lte"])
                    if "gt" in value:  # 큼
                        filters.append(column > value["gt"])
                    if "lt" in value:  # 작음
                        filters.append(column < value["lt"])
                    if "in" in value:  # 리스트 포함 여부
                        filters.append(column.in_(value["in"]))
                    if "not_in" in value:  # 리스트에 포함되지 않는 경우
                        filters.append(~column.in_(value["not_in"]))
                else:  # 단순 동등 비교
                    filters.append(column == value)

            # 필터를 and_로 묶음
            final_filter = and_(*filters)


            # 쿼리 실행
            result = await session.execute(select(self.model).filter(final_filter))
            result_element = result.scalars().one()
            output = {c.name: getattr(result_element, c.name) for c in result_element.__table__.columns}
            return output
    