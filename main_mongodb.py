from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime, timedelta
from api_func.gov import gov_naver_cloud_api, gov_kt_cloud_api, gov_nhn_cloud_api
from api_func.private import (
    private_kt_cloud_api,
    private_naver_cloud_api,
    private_nhn_cloud_api,
)
from databases.connections import Settings
from beanie import PydanticObjectId
from databases.connections import AsyncDatabase
from models.model import (
    UserList,
    CloudList,
    ServiceList,
    CloudTotalChargeList,
    ServiceChargeList,
    TypeChargeList,
    ItemChargeList,
    ThirdPartyChargeList,
    ManagedServiceList,
    OthersServiceList,
)
from sqlalchemy.exc import NoResultFound
from apscheduler.schedulers.background import BackgroundScheduler
from mysql_user_data_setting import BillingDatabaseUpdater

billing_data_updater = BillingDatabaseUpdater()
app = FastAPI()

settings = Settings()

@app.on_event("startup")
async def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(billing_data_updater.update_database, trigger='cron', minute=0)

# 스케줄러 시작
    scheduler.start()


collection_user_list = AsyncDatabase(UserList)
collection_cloud_list = AsyncDatabase(CloudList)
collection_service_list = AsyncDatabase(ServiceList)
collection_cloud_total_charge_list = AsyncDatabase(CloudTotalChargeList)
collection_service_charge_list = AsyncDatabase(ServiceChargeList)
collection_type_charge_list = AsyncDatabase(TypeChargeList)
collection_item_charge_list = AsyncDatabase(ItemChargeList)
# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


def api_select(cloud_info):
    if cloud_info["CLOUD_NAME"] == "NAVER":
        if cloud_info["CLOUD_CLASS"] == "공공":
            return gov_naver_cloud_api
        else:
            return private_naver_cloud_api
    if cloud_info["CLOUD_NAME"] == "KT":
        if cloud_info["CLOUD_CLASS"] == "공공":
            return gov_kt_cloud_api
        else:
            return private_kt_cloud_api
    if cloud_info["CLOUD_NAME"] == "NHN":
        if cloud_info["CLOUD_CLASS"] == "공공":
            return gov_nhn_cloud_api
        else:
            return private_nhn_cloud_api


def generate_month_range(cloud_start_date, start_date, end_date):
    if cloud_start_date > start_date:
        start = datetime.strptime(str(cloud_start_date), "%Y%m")
    else:
        start = datetime.strptime(str(start_date), "%Y%m")

    # 문자열을 datetime 객체로 변환
    end = datetime.strptime(str(end_date), "%Y%m")

    # 결과를 저장할 리스트
    month_list = []

    # start부터 end까지 월 단위로 증가
    while start <= end:
        month_list.append(int(start.strftime("%Y%m")))  # "YYYYMM" 형식으로 저장
        # 한 달 추가
        start += timedelta(days=31)  # 31일을 더하면 다음 달로 넘어감
        start = start.replace(day=1)  # 항상 1일로 설정

    return month_list

def period_check(start_date, end_date, today_date):
    if start_date and end_date:
        if "-" in start_date:
            start_date = int(start_date.replace("-", ""))
        if "-" in end_date:
            end_date = int(end_date.replace("-", ""))
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="시작 날짜가 종료 날짜보다 늦을 수 없습니다."
            )
        if end_date > today_date:
            raise HTTPException(
                status_code=400, detail="조회 종료 날짜는 오늘 날짜 이후일 수 없습니다."
            )
    else:
        one_year_ago = datetime.today() - timedelta(days=365)
        start_date = int(one_year_ago.strftime("%Y%m"))  # 1년 전
        end_date = today_date  # 오늘
    return start_date, end_date

# Load JSON data
def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []





def charge_info_str(total_charge_info):
    total_charge_info["BILL_MONTH_STR"] = (
        str(total_charge_info["BILL_MONTH"])[:4]
        + "년 "
        + str(total_charge_info["BILL_MONTH"])[4:]
        + "월"
    )
    dict_key_list = [i for i in total_charge_info.keys()]
    for dict_key in dict_key_list:
        if "AMT" in dict_key and total_charge_info[dict_key] is not None:
            total_charge_info[dict_key + "_STR"] = (
                f"{int(total_charge_info[dict_key]):,} 원"
            )
    return total_charge_info


async def user_info_load(USER_ID):
    conditions = {"USER_ID": USER_ID}
    user_info = await collection_user_list.get_by_conditions(conditions)
    cloud_list = await collection_cloud_list.gets_by_conditions(conditions)
    user_detail = {
        "USER_ID": user_info["USER_ID"],
        "USER_NAME": user_info["USER_NAME"],
        "CLOUD_ID": [i["CLOUD_ID"] for i in cloud_list],
        "CLOUD_CLASS": [i["CLOUD_CLASS"] for i in cloud_list],
        "CLOUD_NAME": [i["CLOUD_NAME"] for i in cloud_list],
    }
    return user_detail

# Routes
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """메인 페이지"""
    # # Load user data from JSON
    user_list = await collection_user_list.get_all()
    result_list = []
    for user_element in user_list:
        user_element = await user_info_load(user_element["USER_ID"])
        result_list.append(user_element)
        pass
    return templates.TemplateResponse(
        "main.html", {"request": request, "users": result_list}
    )


@app.get("/user_info/{USER_ID}", response_class=HTMLResponse)
async def user_info(
    request: Request,
    USER_ID: str,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None),  # 종료 날짜 (YYYY-MM 형식)
):
    user_detail = await user_info_load(USER_ID)

    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))

    # 조회 기간 검증
    start_date, end_date = period_check(start_date, end_date, today_date)
    data_range = {"start_date": start_date, "end_date": end_date}

    conditions = {"USER_ID": USER_ID}
    cloud_list = await collection_cloud_list.gets_by_conditions(conditions)

    total_charge_list = []
    for cloud_element in cloud_list:
        cloud_start_date = cloud_element["START_DATE"]
        conditions = {
            "CLOUD_ID": cloud_element["CLOUD_ID"]
        }
        total_charge_data = (
            await collection_cloud_total_charge_list.gets_by_conditions(
                conditions
            )
        )
        period_list = generate_month_range(cloud_start_date, start_date, end_date)
        for total_charge_element in total_charge_data:
            if total_charge_element['BILL_MONTH'] in period_list:
                total_charge_element = charge_info_str(total_charge_element)
                total_charge_element["USER_NAME"] = user_detail["USER_NAME"]
                total_charge_element["CLOUD_CLASS"] = cloud_element["CLOUD_CLASS"]
                total_charge_element["CLOUD_NAME"] = cloud_element["CLOUD_NAME"]
                total_charge_list.append(total_charge_element)

    sorted_charge_list = sorted(
        total_charge_list,
        key=lambda x: x["BILL_MONTH"],
        reverse=True,
    )

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_info.html",
        {
            "request": request,
            "user": user_detail,
            "billing_history": sorted_charge_list,
            "date_range": data_range,
        },
    )


@app.get("/billing_list", response_class=HTMLResponse)
async def billing_list(
    request: Request,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None),  # 종료 날짜 (YYYY-MM 형식)
):
    request_dict = dict(await request.form())
    conditions = {}
    cloud_list = await collection_cloud_list.gets_by_conditions(conditions)
    cloud_dict = {}
    for cloud_element in cloud_list:
        cloud_dict[dict(cloud_element)["cloud_id"]] = {
            "cloud_name": dict(cloud_element)["cloud_name"],
            "cloud_class": dict(cloud_element)["cloud_class"],
            "user_name": dict(cloud_element)["user_name"],
        }

    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))

    # 조회 기간 검증
    start_date, end_date = period_check(start_date, end_date, today_date)
    date_range = {"start_date": start_date, "end_date": end_date}

    """청구 목록 페이지"""
    conditions = {
        "bill_month": {"$gte": start_date, "$lte": end_date},
    }
    total_charge_list = await collection_cloud_total_charge_list.gets_by_conditions(
        conditions
    )
    total_charge_list = [dict(i) for i in total_charge_list]
    for total_charge_info in total_charge_list:
        total_charge_info = charge_info_str(total_charge_info)
        cloud_id = "-".join(total_charge_info["charge_id"].split("-")[:2])
        total_charge_info["user_name"] = cloud_dict[cloud_id]["user_name"]
        total_charge_info["cloud_name"] = cloud_dict[cloud_id]["cloud_name"]
        total_charge_info["cloud_class"] = cloud_dict[cloud_id]["cloud_class"]
    sorted_charge_list = sorted(
        total_charge_list,
        key=lambda x: x["bill_month"],
        reverse=True,
    )
    return templates.TemplateResponse(
        "billing_list.html",
        {
            "request": request,
            "date_range": date_range,
            "total_charge_list": sorted_charge_list,
        },
    )


@app.get("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(
    request: Request,
    charge_id: str,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None),  # 종료 날짜 (YYYY-MM 형식)
):

    conditions = {"TOTAL_CHARGE_ID": charge_id}
    total_charge_element = await collection_cloud_total_charge_list.get_by_conditions(
        conditions
    )
    conditions = {"CLOUD_ID": total_charge_element["CLOUD_ID"]}
    cloud_info = await collection_cloud_list.get_by_conditions(conditions)
    conditions = {"USER_ID": cloud_info["USER_ID"]}
    user_info = await collection_user_list.get_by_conditions(conditions)

    user_dict = {
        "USER_ID": user_info["USER_ID"],
        "USER_NAME": user_info["USER_NAME"],
        "CLOUD_CLASS": cloud_info["CLOUD_CLASS"],
        "CLOUD_NAME": cloud_info["CLOUD_NAME"],
    }
    total_charge_info = charge_info_str(total_charge_element)
    service_charge_list = []
    conditions = {"TOTAL_CHARGE_ID": total_charge_info["TOTAL_CHARGE_ID"]}
    service_charge_list = await collection_service_charge_list.gets_by_conditions(conditions)
    for service_charge_info in service_charge_list:
        service_charge_id = service_charge_info['SERVICE_CHARGE_ID']
        conditions = {"SERVICE_CHARGE_ID": service_charge_id}
        type_charge_list = await collection_type_charge_list.gets_by_conditions(conditions)
        type_list = [] 
        type_charge_length = 1
        for type_charge_info in type_charge_list:
            type_charge_id = type_charge_info['TYPE_CHARGE_ID']
            conditions = {"TYPE_CHARGE_ID": type_charge_id}
            item_charge_list = await collection_item_charge_list.gets_by_conditions(conditions)

            type_charge_info['item_list'] = item_charge_list
            item_charge_length = len(item_charge_list) + 1
            type_charge_info['ITEM_CHARGE_LENGH'] = item_charge_length
            type_charge_length += item_charge_length
            type_list.append(type_charge_info)  
        service_charge_info['TYPE_CHARGE_LENGH'] = type_charge_length
        service_charge_info['type_list'] = type_list
        pass
    return templates.TemplateResponse(
        "billing_info.html",
        {
            "request": request,
            "user": user_dict,
            "total_charge_info": total_charge_info,
            "service_charge_list": service_charge_list,
        },
    )


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
