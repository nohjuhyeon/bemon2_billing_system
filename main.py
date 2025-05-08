from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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
    OtherServiceList,
)
from apscheduler.schedulers.background import BackgroundScheduler
from mysql_user_data_setting import BillingDatabaseUpdater

app = FastAPI()
settings = Settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files 설정
app.mount("/css", StaticFiles(directory="resources/css/"), name="static_css")
app.mount("/js", StaticFiles(directory="resources/js/"), name="static_js")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def init_scheduler():
    billing_data_updater = BillingDatabaseUpdater()
    scheduler = BackgroundScheduler()
    scheduler.add_job(billing_data_updater.update_database, trigger="cron", minute=0)

    # 스케줄러 시작
    scheduler.start()


collection_user_list = AsyncDatabase(UserList)
collection_cloud_list = AsyncDatabase(CloudList)
collection_service_list = AsyncDatabase(ServiceList)
collection_cloud_total_charge_list = AsyncDatabase(CloudTotalChargeList)
collection_third_party_charge_list = AsyncDatabase(ThirdPartyChargeList)
collection_managed_service_charge_list = AsyncDatabase(ManagedServiceList)
collection_other_service_charge_list = AsyncDatabase(OtherServiceList)
collection_service_charge_list = AsyncDatabase(ServiceChargeList)
collection_type_charge_list = AsyncDatabase(TypeChargeList)
collection_item_charge_list = AsyncDatabase(ItemChargeList)


def charge_info_str(total_charge_info):
    dict_key_list = [i for i in total_charge_info.keys()]
    for dict_key in dict_key_list:
        if "BILL_MONTH" in dict_key and total_charge_info[dict_key] is not None:
            total_charge_info["BILL_MONTH_STR"] = (
                str(total_charge_info["BILL_MONTH"])[:4]
                + "년 "
                + str(total_charge_info["BILL_MONTH"])[4:]
                + "월"
            )
        elif "AMT" in dict_key and total_charge_info[dict_key] is not None:
            total_charge_info[dict_key + "_STR"] = (
                f"{int(total_charge_info[dict_key]):,} 원"
            )
    return total_charge_info


def filter_dict_create(form_list):
    form_list = form_list._list
    category_list = list()
    cloud_list = list()
    condition_dict = {}
    for form_data in form_list:
        if form_data[0] == "customer_name":
            condition_dict["user_name"] = form_data[1]
        elif form_data[0] == "category":
            category_list.append(form_data[1])
        elif form_data[0] == "start_date":
            start_date = int(form_data[1].replace("-", ""))
            condition_dict["start_date"] = start_date
        elif form_data[0] == "end_date":
            end_date = int(form_data[1].replace("-", ""))
            condition_dict["end_date"] = end_date
        elif form_data[0] == "cloud-company":
            cloud_list.append(form_data[1])
    condition_dict["class_list"] = list(category_list)
    condition_dict["cloud_list"] = list(cloud_list)
    return condition_dict


async def get_user_info(USER_ID):
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
        user_element = await get_user_info(user_element["USER_ID"])
        result_list.append(user_element)
        pass
    return templates.TemplateResponse(
        "main.html",
        {"request": request, "users": result_list, "filter_condition": None},
    )


# Routes
@app.post("/", response_class=HTMLResponse)
async def main(request: Request):
    """메인 페이지"""
    form_list = await request.form()
    condition_dict = filter_dict_create(form_list)

    user_list = await collection_user_list.get_all()
    result_list = []
    for user_element in user_list:
        user_element = await get_user_info(user_element["USER_ID"])
        class_intersection = set(user_element["CLOUD_CLASS"]) & set(
            condition_dict["class_list"]
        )
        cloud_intersection = set(user_element["CLOUD_NAME"]) & set(
            condition_dict["cloud_list"]
        )
        if (
            condition_dict["user_name"] in user_element["USER_NAME"]
            and class_intersection
            and cloud_intersection
        ):
            result_list.append(user_element)
            pass
    return templates.TemplateResponse(
        "main.html",
        {"request": request, "users": result_list, "filter_condition": condition_dict},
    )


@app.get("/user_info/{USER_ID}", response_class=HTMLResponse)
async def user_info(request: Request, USER_ID: str):
    user_detail = await get_user_info(USER_ID)

    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))
    one_year_ago = today - timedelta(days=365)
    start_date = int(one_year_ago.strftime("%Y%m"))

    date_range = {"start_date": start_date, "end_date": today_date}

    conditions = {"USER_ID": USER_ID}
    cloud_list = await collection_cloud_list.gets_by_conditions(conditions)

    total_charge_list = []
    for cloud_element in cloud_list:
        conditions = {"CLOUD_ID": cloud_element["CLOUD_ID"]}
        total_charge_data = await collection_cloud_total_charge_list.gets_by_conditions(
            conditions
        )

        for total_charge_element in total_charge_data:
            total_charge_element = charge_info_str(total_charge_element)
            total_charge_element["USER_NAME"] = user_detail["USER_NAME"]
            total_charge_element["CLOUD_CLASS"] = cloud_element["CLOUD_CLASS"]
            total_charge_element["CLOUD_NAME"] = cloud_element["CLOUD_NAME"]
            total_charge_list.append(total_charge_element)

    sorted_charge_list = sorted(
        total_charge_list, key=lambda x: x["BILL_MONTH"], reverse=True
    )

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_info.html",
        {
            "request": request,
            "user": user_detail,
            "billing_history": sorted_charge_list,
            "date_range": date_range,
        },
    )


@app.post("/user_info/{USER_ID}", response_class=HTMLResponse)
async def user_info(request: Request, USER_ID: str):
    form_list = await request.form()
    condition_dict = filter_dict_create(form_list)

    date_range = {
        "start_date": condition_dict["start_date"],
        "end_date": condition_dict["end_date"],
    }

    user_detail = await get_user_info(USER_ID)

    conditions = {"USER_ID": USER_ID}
    cloud_list = await collection_cloud_list.gets_by_conditions(conditions)

    total_charge_list = []
    for cloud_element in cloud_list:
        conditions = {"CLOUD_ID": cloud_element["CLOUD_ID"]}
        total_charge_data = await collection_cloud_total_charge_list.gets_by_conditions(
            conditions
        )

        for total_charge_element in total_charge_data:
            if (
                total_charge_element["BILL_MONTH"] >= date_range["start_date"]
                and total_charge_element["BILL_MONTH"] <= date_range["end_date"]
            ):
                total_charge_element = charge_info_str(total_charge_element)
                total_charge_element["USER_NAME"] = user_detail["USER_NAME"]
                total_charge_element["CLOUD_CLASS"] = cloud_element["CLOUD_CLASS"]
                total_charge_element["CLOUD_NAME"] = cloud_element["CLOUD_NAME"]
                total_charge_list.append(total_charge_element)

    sorted_charge_list = sorted(
        total_charge_list, key=lambda x: x["BILL_MONTH"], reverse=True
    )

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_info.html",
        {
            "request": request,
            "user": user_detail,
            "billing_history": sorted_charge_list,
            "date_range": date_range,
        },
    )


@app.get("/billing_list", response_class=HTMLResponse)
async def billing_list(request: Request):

    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))
    one_year_ago = today - timedelta(days=365)
    start_date = int(one_year_ago.strftime("%Y%m"))

    # 조회 기간 검증
    date_range = {"start_date": start_date, "end_date": today_date}
    user_elements = await collection_user_list.get_all()
    total_charge_list = []
    for user_info in user_elements:
        user_id = user_info["USER_ID"]
        user_name = user_info["USER_NAME"]
        cloud_conditions = {"USER_ID": user_id}
        cloud_elements = await collection_cloud_list.gets_by_conditions(
            cloud_conditions
        )
        for cloud_info in cloud_elements:
            cloud_id = cloud_info["CLOUD_ID"]
            cloud_class = cloud_info["CLOUD_CLASS"]
            cloud_name = cloud_info["CLOUD_NAME"]
            total_charge_conditions = {"CLOUD_ID": cloud_id}
            total_charge_elements = (
                await collection_cloud_total_charge_list.gets_by_conditions(
                    total_charge_conditions
                )
            )
            for total_charge_info in total_charge_elements:
                total_charge_info = charge_info_str(total_charge_info)
                total_charge_info["USER_NAME"] = user_name
                total_charge_info["CLOUD_CLASS"] = cloud_class
                total_charge_info["CLOUD_NAME"] = cloud_name
                total_charge_list.append(total_charge_info)

        pass

    sorted_charge_list = sorted(
        total_charge_list,
        key=lambda x: x["BILL_MONTH"],
        reverse=True,
    )
    return templates.TemplateResponse(
        "billing_list.html",
        {
            "request": request,
            "date_range": date_range,
            "total_charge_list": sorted_charge_list,
            "filter_condition": None,
        },
    )


@app.post("/billing_list", response_class=HTMLResponse)
async def billing_list(request: Request):
    form_list = await request.form()
    condition_dict = filter_dict_create(form_list)

    date_range = {
        "start_date": condition_dict["start_date"],
        "end_date": condition_dict["end_date"],
    }

    user_elements = await collection_user_list.get_all()
    total_charge_list = []
    for user_info in user_elements:
        user_id = user_info["USER_ID"]
        user_name = user_info["USER_NAME"]
        if condition_dict["user_name"] in user_name:
            cloud_conditions = {"USER_ID": user_id}
            cloud_elements = await collection_cloud_list.gets_by_conditions(
                cloud_conditions
            )
            for cloud_info in cloud_elements:
                cloud_id = cloud_info["CLOUD_ID"]
                cloud_class = cloud_info["CLOUD_CLASS"]
                cloud_name = cloud_info["CLOUD_NAME"]
                if cloud_class in condition_dict['class_list'] and cloud_name in condition_dict["cloud_list"]:
                    total_charge_conditions = {"CLOUD_ID": cloud_id}
                    total_charge_elements = (
                        await collection_cloud_total_charge_list.gets_by_conditions(
                            total_charge_conditions
                        )
                    )
                    for total_charge_info in total_charge_elements:
                        if (
                            total_charge_info["BILL_MONTH"] >= date_range["start_date"]
                            and total_charge_info["BILL_MONTH"]
                            <= date_range["end_date"]
                        ):
                            total_charge_info = charge_info_str(total_charge_info)
                            total_charge_info["USER_NAME"] = user_name
                            total_charge_info["CLOUD_CLASS"] = cloud_class
                            total_charge_info["CLOUD_NAME"] = cloud_name
                            total_charge_list.append(total_charge_info)

    sorted_charge_list = sorted(
        total_charge_list,
        key=lambda x: x["BILL_MONTH"],
        reverse=True,
    )
    return templates.TemplateResponse(
        "billing_list.html",
        {
            "request": request,
            "date_range": date_range,
            "total_charge_list": sorted_charge_list,
            "filter_condition": condition_dict,
        },
    )


@app.get("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(request: Request, charge_id: str):

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
    conditions = {"TOTAL_CHARGE_ID": total_charge_info["TOTAL_CHARGE_ID"]}
    cloud_service_charge_list = await collection_service_charge_list.gets_by_conditions(
        conditions
    )
    third_party_charge_list = await collection_third_party_charge_list.gets_by_conditions(conditions)
    managed_service_charge_list = await collection_managed_service_charge_list.gets_by_conditions(conditions)
    other_service_charge_list = await collection_other_service_charge_list.gets_by_conditions(conditions)
    for cloud_service_charge_info in cloud_service_charge_list:
        service_charge_id = cloud_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
        conditions = {"CLOUD_SERVICE_CHARGE_ID": service_charge_id}
        type_charge_list = await collection_type_charge_list.gets_by_conditions(
            conditions
        )
        type_list = []
        type_charge_length = 1
        for type_charge_info in type_charge_list:
            type_charge_id = type_charge_info["TYPE_CHARGE_ID"]

            conditions = {"TYPE_CHARGE_ID": type_charge_id}
            item_charge_list = await collection_item_charge_list.gets_by_conditions(
                conditions
            )
            item_charge_list = [charge_info_str(item_info) for item_info in item_charge_list]
            type_charge_info["item_list"] = item_charge_list
            item_charge_length = len(item_charge_list) + 1
            type_charge_info["ITEM_CHARGE_LENGH"] = item_charge_length
            type_charge_length += item_charge_length
            type_charge_info = charge_info_str(type_charge_info)
            type_list.append(type_charge_info)
        cloud_service_charge_info["TYPE_CHARGE_LENGH"] = type_charge_length
        cloud_service_charge_info["type_list"] = type_list
        cloud_service_charge_info = charge_info_str(cloud_service_charge_info)
        pass
    return templates.TemplateResponse(
        "billing_info.html",
        {
            "request": request,
            "user": user_dict,
            "total_charge_info": total_charge_info,
            "cloud_service_charge_list": cloud_service_charge_list,
            "managed_service_charge_list": managed_service_charge_list,
            "third_party_charge_list": third_party_charge_list,
            "other_service_charge_list": other_service_charge_list,
            
        },
    )


@app.post("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(request: Request, charge_id: str):

    form_list = await request.form()
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
    conditions = {"TOTAL_CHARGE_ID": total_charge_info["TOTAL_CHARGE_ID"]}
    cloud_service_charge_list = await collection_service_charge_list.gets_by_conditions(
        conditions
    )
    third_party_charge_list = await collection_third_party_charge_list.gets_by_conditions(conditions)
    managed_service_charge_list = await collection_managed_service_charge_list.gets_by_conditions(conditions)
    other_service_charge_list = await collection_other_service_charge_list.gets_by_conditions(conditions)
    for cloud_service_charge_info in cloud_service_charge_list:
        service_charge_id = cloud_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
        conditions = {"CLOUD_SERVICE_CHARGE_ID": service_charge_id}
        type_charge_list = await collection_type_charge_list.gets_by_conditions(
            conditions
        )
        type_list = []
        type_charge_length = 1
        for type_charge_info in type_charge_list:
            type_charge_id = type_charge_info["TYPE_CHARGE_ID"]

            conditions = {"TYPE_CHARGE_ID": type_charge_id}
            item_charge_list = await collection_item_charge_list.gets_by_conditions(
                conditions
            )
            item_charge_list = [charge_info_str(item_info) for item_info in item_charge_list]
            type_charge_info["item_list"] = item_charge_list
            item_charge_length = len(item_charge_list) + 1
            type_charge_info["ITEM_CHARGE_LENGH"] = item_charge_length
            type_charge_length += item_charge_length
            type_charge_info = charge_info_str(type_charge_info)
            type_list.append(type_charge_info)
        cloud_service_charge_info["TYPE_CHARGE_LENGH"] = type_charge_length
        cloud_service_charge_info["type_list"] = type_list
        cloud_service_charge_info = charge_info_str(cloud_service_charge_info)
        pass
    return templates.TemplateResponse(
        "billing_info.html",
        {
            "request": request,
            "user": user_dict,
            "total_charge_info": total_charge_info,
            "cloud_service_charge_list": cloud_service_charge_list,
            "managed_service_charge_list": managed_service_charge_list,
            "third_party_charge_list": third_party_charge_list,
            "other_service_charge_list": other_service_charge_list,
            
        },
    )
    
# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
