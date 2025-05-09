from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime, timedelta
from databases.connections import Settings
from charge_info_manager import ChargeInfoManager
from apscheduler.schedulers.background import BackgroundScheduler
from mysql_user_data_setting import BillingDatabaseUpdater
import asyncio

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

charge_manager = ChargeInfoManager()
@app.on_event("startup")
async def init_scheduler():
    billing_data_updater = BillingDatabaseUpdater()
    scheduler = BackgroundScheduler()
    scheduler.add_job(billing_data_updater.update_database, trigger="cron", minute=0)

    # 스케줄러 시작
    scheduler.start()


# Routes
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """메인 페이지"""
    # # Load user data from JSON
    user_list = await charge_manager.collection_user_list.get_all()
    result_list = []
    for user_element in user_list:
        user_element = await charge_manager.get_user_info_by_user_id(user_element["USER_ID"])
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
    condition_dict = charge_manager.filter_dict_create(form_list)

    user_list = await charge_manager.collection_user_list.get_all()
    result_list = []
    for user_element in user_list:
        user_element = await charge_manager.get_user_info_by_user_id(user_element["USER_ID"])
        class_intersection = set(user_element["CLOUD_CLASS"]) & set(condition_dict["class_list"])
        cloud_intersection = set(user_element["CLOUD_NAME"]) & set(condition_dict["cloud_list"])
        if (condition_dict["user_name"] in user_element["USER_NAME"] and class_intersection and cloud_intersection):
            result_list.append(user_element)
            pass
    return templates.TemplateResponse(
        "main.html",
        {"request": request, "users": result_list, "filter_condition": condition_dict},
    )


@app.get("/user_info/{USER_ID}", response_class=HTMLResponse)
async def user_info(request: Request, USER_ID: str):
    user_detail = await charge_manager.get_user_info_by_user_id(USER_ID)

    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))
    one_year_ago = today - timedelta(days=365)
    start_date = int(one_year_ago.strftime("%Y%m"))

    date_range = {"start_date": start_date, "end_date": today_date}

    conditions = {"USER_ID": {"eq": USER_ID}}
    cloud_list = await charge_manager.collection_cloud_list.gets_by_conditions(conditions)

    total_charge_list = []
    for cloud_element in cloud_list:
        conditions = {"CLOUD_ID": {"eq": cloud_element["CLOUD_ID"]}}
        total_charge_data = await charge_manager.collection_cloud_total_charge_list.gets_by_conditions(conditions)

        for total_charge_element in total_charge_data:
            total_charge_element = charge_manager.charge_info_str(total_charge_element)
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
    condition_dict = charge_manager.filter_dict_create(form_list)

    date_range = {
        "start_date": condition_dict["start_date"],
        "end_date": condition_dict["end_date"],
    }

    user_detail = await charge_manager.get_user_info_by_user_id(USER_ID)

    conditions = {"USER_ID": USER_ID}
    cloud_list = await charge_manager.collection_cloud_list.gets_by_conditions(conditions)

    total_charge_list = []
    for cloud_element in cloud_list:
        conditions = {
            "CLOUD_ID": {"eq": cloud_element["CLOUD_ID"]},
            "BILL_MONTH":{"gte": date_range["start_date"],"lte": date_range["end_date"]}
            }
        total_charge_data = await charge_manager.collection_cloud_total_charge_list.gets_by_conditions(conditions)
        for total_charge_element in total_charge_data:
            total_charge_element = charge_manager.charge_info_str(total_charge_element)
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
    user_elements = await charge_manager.collection_user_list.get_all()
    total_charge_list = []
    for user_info in user_elements:
        user_id = user_info["USER_ID"]
        user_name = user_info["USER_NAME"]
        cloud_conditions = {"USER_ID": user_id}
        cloud_elements = await charge_manager.collection_cloud_list.gets_by_conditions(
            cloud_conditions
        )
        for cloud_info in cloud_elements:
            cloud_id = cloud_info["CLOUD_ID"]
            cloud_class = cloud_info["CLOUD_CLASS"]
            cloud_name = cloud_info["CLOUD_NAME"]
            total_charge_conditions = {"CLOUD_ID": cloud_id}
            total_charge_elements = (
                await charge_manager.collection_cloud_total_charge_list.gets_by_conditions(
                    total_charge_conditions
                )
            )
            for total_charge_info in total_charge_elements:
                total_charge_info = charge_manager.charge_info_str(total_charge_info)
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
    condition_dict = charge_manager.filter_dict_create(form_list)

    date_range = {
        "start_date": condition_dict["start_date"],
        "end_date": condition_dict["end_date"],
    }

    user_elements = await charge_manager.collection_user_list.get_all()
    total_charge_list = []
    for user_info in user_elements:
        user_id = user_info["USER_ID"]
        user_name = user_info["USER_NAME"]
        if condition_dict["user_name"] in user_name:
            cloud_conditions = {"USER_ID": user_id}
            cloud_elements = await charge_manager.collection_cloud_list.gets_by_conditions(
                cloud_conditions
            )
            for cloud_info in cloud_elements:
                cloud_id = cloud_info["CLOUD_ID"]
                cloud_class = cloud_info["CLOUD_CLASS"]
                cloud_name = cloud_info["CLOUD_NAME"]
                if cloud_class in condition_dict['class_list'] and cloud_name in condition_dict["cloud_list"]:
                    total_charge_conditions = {"CLOUD_ID": cloud_id}
                    total_charge_elements = (
                        await charge_manager.collection_cloud_total_charge_list.gets_by_conditions(
                            total_charge_conditions
                        )
                    )
                    for total_charge_info in total_charge_elements:
                        if (
                            total_charge_info["BILL_MONTH"] >= date_range["start_date"]
                            and total_charge_info["BILL_MONTH"]
                            <= date_range["end_date"]
                        ):
                            total_charge_info = charge_manager.charge_info_str(total_charge_info)
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
    total_charge_element = await charge_manager.collection_cloud_total_charge_list.get_by_conditions(conditions)

    total_charge_info = charge_manager.charge_info_str(total_charge_element)
    conditions = {"TOTAL_CHARGE_ID": total_charge_info["TOTAL_CHARGE_ID"]}

    cloud_service_charge_list = await charge_manager.collection_service_charge_list.gets_by_conditions(conditions)
    third_party_charge_list = await charge_manager.collection_third_party_charge_list.gets_by_conditions(conditions)
    managed_service_charge_list = await charge_manager.collection_managed_service_charge_list.gets_by_conditions(conditions)
    other_service_charge_list = await charge_manager.collection_other_service_charge_list.gets_by_conditions(conditions)

    user_dict = await charge_manager.get_user_info_by_cloud_id(total_charge_element)
    cloud_service_charge_list = await charge_manager.get_cloud_service_charge(cloud_service_charge_list)
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
    total_charge_element = await charge_manager.collection_cloud_total_charge_list.get_by_conditions(
        conditions
    )
    
    
    conditions = {"CLOUD_ID": total_charge_element["CLOUD_ID"]}
    cloud_info = await charge_manager.collection_cloud_list.get_by_conditions(conditions)
    conditions = {"USER_ID": cloud_info["USER_ID"]}
    user_info = await charge_manager.collection_user_list.get_by_conditions(conditions)

    user_dict = {
        "USER_ID": user_info["USER_ID"],
        "USER_NAME": user_info["USER_NAME"],
        "CLOUD_CLASS": cloud_info["CLOUD_CLASS"],
        "CLOUD_NAME": cloud_info["CLOUD_NAME"],
    }
    total_charge_info = charge_manager.charge_info_str(total_charge_element)
    conditions = {"TOTAL_CHARGE_ID": total_charge_info["TOTAL_CHARGE_ID"]}
    cloud_service_charge_list = await charge_manager.collection_service_charge_list.gets_by_conditions(
        conditions
    )
    third_party_charge_list = await charge_manager.collection_third_party_charge_list.gets_by_conditions(conditions)
    managed_service_charge_list = await charge_manager.collection_managed_service_charge_list.gets_by_conditions(conditions)
    other_service_charge_list = await charge_manager.collection_other_service_charge_list.gets_by_conditions(conditions)
    for cloud_service_charge_info in cloud_service_charge_list:
        service_charge_id = cloud_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
        conditions = {"CLOUD_SERVICE_CHARGE_ID": service_charge_id}
        type_charge_list = await charge_manager.collection_type_charge_list.gets_by_conditions(
            conditions
        )
        type_list = []
        type_charge_length = 1
        for type_charge_info in type_charge_list:
            type_charge_id = type_charge_info["TYPE_CHARGE_ID"]

            conditions = {"TYPE_CHARGE_ID": type_charge_id}
            item_charge_list = await charge_manager.collection_item_charge_list.gets_by_conditions(
                conditions
            )
            item_charge_list = [charge_manager.charge_info_str(item_info) for item_info in item_charge_list]
            type_charge_info["item_list"] = item_charge_list
            item_charge_length = len(item_charge_list) + 1
            type_charge_info["ITEM_CHARGE_LENGH"] = item_charge_length
            type_charge_length += item_charge_length
            type_charge_info = charge_manager.charge_info_str(type_charge_info)
            type_list.append(type_charge_info)
        cloud_service_charge_info["TYPE_CHARGE_LENGH"] = type_charge_length
        cloud_service_charge_info["type_list"] = type_list
        cloud_service_charge_info = charge_manager.charge_info_str(cloud_service_charge_info)
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
