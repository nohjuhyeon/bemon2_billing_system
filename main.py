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
    cloud_list_conditions = {}
    result_list = await charge_manager.get_user_list(user_list,cloud_list_conditions)

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

    user_list_conditions = {"USER_NAME": {"like": condition_dict['user_name']}}
    user_list = await charge_manager.collection_user_list.gets_by_conditions(user_list_conditions)
    cloud_list_conditions = {"CLOUD_CLASS": {"in": condition_dict['class_list']},"CLOUD_NAME": {"in": condition_dict['cloud_list']}}

    result_list = await charge_manager.get_user_list(user_list,cloud_list_conditions)
    
    return templates.TemplateResponse(
        "main.html",
        {"request": request, "users": result_list, "filter_condition": condition_dict},
    )


@app.get("/user_billing/{USER_ID}", response_class=HTMLResponse)
async def user_billing(request: Request, USER_ID: str):
    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))
    one_year_ago = today - timedelta(days=365)
    start_date = int(one_year_ago.strftime("%Y%m"))

    date_range = {"start_date": start_date, "end_date": today_date}

    user_info = await charge_manager.get_user_info(USER_ID)
    user_billing_list = await charge_manager.get_cloud_charge_list(USER_ID,date_range)
    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_billing.html",
        {
            "request": request,
            "user": user_info,
            "billing_history": user_billing_list,
            "date_range": date_range,
        },
    )


@app.post("/user_billing/{USER_ID}", response_class=HTMLResponse)
async def user_billing(request: Request, USER_ID: str):
    form_list = await request.form()
    condition_dict = charge_manager.filter_dict_create(form_list)

    date_range = {"start_date": condition_dict["start_date"],"end_date": condition_dict["end_date"]}
    
    user_info = await charge_manager.get_user_info(USER_ID)
    user_billing_list = await charge_manager.get_cloud_charge_list(USER_ID,date_range)

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_billing.html",
        {
            "request": request,
            "user": user_info,
            "billing_history": user_billing_list,
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
    date_range = {"start_date": start_date, "end_date": today_date}
    
    user_list = await charge_manager.collection_user_list.get_all()
    cloud_list_conditions = {}
    
    total_billing_list = await charge_manager.get_billing_list(user_list,cloud_list_conditions,date_range)
    return templates.TemplateResponse(
        "billing_list.html",
        {
            "request": request,
            "date_range": date_range,
            "total_charge_list": total_billing_list,
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

    user_list_conditions = {"USER_NAME": {"like": condition_dict['user_name']}}
    cloud_list_conditions = {"CLOUD_CLASS": {"in": condition_dict['class_list']},"CLOUD_NAME": {"in": condition_dict['cloud_list']}}

    user_list = await charge_manager.collection_user_list.gets_by_conditions(user_list_conditions)
    total_billing_list = await charge_manager.get_billing_list(user_list,cloud_list_conditions,date_range)

    return templates.TemplateResponse(
        "billing_list.html",
        {
            "request": request,
            "date_range": date_range,
            "total_charge_list": total_billing_list,
            "filter_condition": condition_dict,
        },
    )

@app.get("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(request: Request, charge_id: str):
    total_charge_conditions = {"TOTAL_CHARGE_ID": {"eq": charge_id}}

    total_charge_element = await charge_manager.collection_cloud_total_charge_list.get_by_conditions(total_charge_conditions)
    total_charge_info = charge_manager.charge_info_str(total_charge_element)

    cloud_service_charge_list = await charge_manager.collection_service_charge_list.gets_by_conditions(total_charge_conditions)
    cloud_service_charge_list = [charge_manager.charge_info_str(cloud_service_charge_info) for cloud_service_charge_info in cloud_service_charge_list]
    third_party_charge_list = await charge_manager.collection_third_party_charge_list.gets_by_conditions(total_charge_conditions)
    third_party_charge_list = [charge_manager.charge_info_str(third_party_charge_info) for third_party_charge_info in third_party_charge_list]
    managed_service_charge_list = await charge_manager.collection_managed_service_charge_list.gets_by_conditions(total_charge_conditions)
    managed_service_charge_list = [charge_manager.charge_info_str(managed_service_charge_info) for managed_service_charge_info in managed_service_charge_list]
    other_service_charge_list = await charge_manager.collection_other_service_charge_list.gets_by_conditions(total_charge_conditions)
    other_service_charge_list = [charge_manager.charge_info_str(other_service_charge_info) for other_service_charge_info in other_service_charge_list]

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

    update_data = await request.form()
    await charge_manager.billing_info_update(update_data,charge_id)

    total_charge_conditions = {"TOTAL_CHARGE_ID": {"eq": charge_id}}

    total_charge_element = await charge_manager.collection_cloud_total_charge_list.get_by_conditions(total_charge_conditions)
    total_charge_info = charge_manager.charge_info_str(total_charge_element)

    cloud_service_charge_list = await charge_manager.collection_service_charge_list.gets_by_conditions(total_charge_conditions)
    cloud_service_charge_list = [charge_manager.charge_info_str(cloud_service_charge_info) for cloud_service_charge_info in cloud_service_charge_list]
    third_party_charge_list = await charge_manager.collection_third_party_charge_list.gets_by_conditions(total_charge_conditions)
    third_party_charge_list = [charge_manager.charge_info_str(third_party_charge_info) for third_party_charge_info in third_party_charge_list]
    managed_service_charge_list = await charge_manager.collection_managed_service_charge_list.gets_by_conditions(total_charge_conditions)
    managed_service_charge_list = [charge_manager.charge_info_str(managed_service_charge_info) for managed_service_charge_info in managed_service_charge_list]
    other_service_charge_list = await charge_manager.collection_other_service_charge_list.gets_by_conditions(total_charge_conditions)
    other_service_charge_list = [charge_manager.charge_info_str(other_service_charge_info) for other_service_charge_info in other_service_charge_list]

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
    
# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
