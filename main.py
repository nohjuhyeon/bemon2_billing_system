from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime, timedelta
from databases.connections import Settings
from bemon_manage_func.charge_info_manager import ChargeInfoManager
from bemon_manage_func.invoice_create_manager import InvoiceCreateManager
from apscheduler.schedulers.background import BackgroundScheduler
from data_setting.mysql_user_data_setting import BillingDatabaseUpdater
from fastapi.responses import FileResponse
import asyncio
import os 

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
app.mount("/image", StaticFiles(directory="resources/image/"), name="static_css")
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


@app.get("/user_billing/{CLOUD_ID}", response_class=HTMLResponse)
async def user_billing(request: Request, CLOUD_ID: str):
    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))
    one_year_ago = today - timedelta(days=365)
    start_date = int(one_year_ago.strftime("%Y%m"))

    date_range = {"start_date": start_date, "end_date": today_date}
    user_info,user_billing_list = await charge_manager.get_cloud_charge_list(CLOUD_ID,date_range)
    date_range['start_date'] = str(date_range['start_date'])[:4]+'-' + str(date_range['start_date'])[-2:]
    date_range['end_date'] = str(date_range['end_date'])[:4]+'-' + str(date_range['end_date'])[-2:]
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


@app.post("/user_billing/{CLOUD_ID}", response_class=HTMLResponse)
async def user_billing(request: Request, CLOUD_ID: str):
    form_list = await request.form()
    condition_dict = charge_manager.filter_dict_create(form_list)

    if 'start_date' in condition_dict.keys() and 'end_date' in condition_dict.keys():
        start_date = condition_dict['start_date']
        end_date = condition_dict['end_date']
    else:
        today = datetime.today()
        end_date = int(today.strftime("%Y%m"))
        one_year_ago = today - timedelta(days=365)
        start_date = int(one_year_ago.strftime("%Y%m"))

    date_range = {"start_date": start_date,"end_date": end_date}
    
    user_info,user_billing_list = await charge_manager.get_cloud_charge_list(CLOUD_ID,date_range)
    date_range['start_date'] = str(date_range['start_date'])[:4]+'-' + str(date_range['start_date'])[-2:]
    date_range['end_date'] = str(date_range['end_date'])[:4]+'-' + str(date_range['end_date'])[-2:]
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

@app.get("/user_manage/{CLOUD_ID}", response_class=HTMLResponse)
async def user_manage(request: Request, CLOUD_ID: str):
    # 오늘 날짜 계산

    user_info,third_party_list,managed_service_list,other_service_list = await charge_manager.get_cloud_info(CLOUD_ID)
    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_manage.html",
        {
            "request": request,
            "user": user_info,
            'third_party_list':third_party_list,
            'managed_service_list':managed_service_list,
            'other_service_list':other_service_list,
        },
    )


@app.post("/user_manage/{CLOUD_ID}", response_class=HTMLResponse)
async def user_manage(request: Request, CLOUD_ID: str):
    form_list = await request.form()
    await charge_manager.billing_info_update(form_list,CLOUD_ID)
        
    user_info,third_party_list,managed_service_list,other_service_list = await charge_manager.get_cloud_info(CLOUD_ID)

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse(
        "user_manage.html",
        {
            "request": request,
            "user": user_info,
            'third_party_list':third_party_list,
            'managed_service_list':managed_service_list,
            'other_service_list':other_service_list
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
    date_range['start_date'] = str(date_range['start_date'])[:4]+'-' + str(date_range['start_date'])[-2:]
    date_range['end_date'] = str(date_range['end_date'])[:4]+'-' + str(date_range['end_date'])[-2:]
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
    date_range['start_date'] = str(date_range['start_date'])[:4]+'-' + str(date_range['start_date'])[-2:]
    date_range['end_date'] = str(date_range['end_date'])[:4]+'-' + str(date_range['end_date'])[-2:]

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
    request_dict = await charge_manager.get_billing_info_dict(charge_id)
    request_dict['request'] = request
    return templates.TemplateResponse("billing_info.html",request_dict)


@app.post("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(request: Request, charge_id: str):

    update_data = await request.form()
    await charge_manager.billing_info_update(update_data,charge_id)

    request_dict = await charge_manager.get_billing_info_dict(charge_id)
    request_dict['request'] = request
    return templates.TemplateResponse("billing_info.html",request_dict)

@app.get("/billing_info/download-excel/{charge_id}")
async def download_excel(request: Request, charge_id: str):
    billing_dict = await charge_manager.get_billing_info_dict(charge_id)
    invoice_manager= InvoiceCreateManager(billing_dict)
    file_path = invoice_manager.invoice_create()
    today = datetime.today()
    today_date = today.strftime("%Y%m%d")
    file_name = "이용내역서_"+billing_dict['user']['CLOUD_NAME']+"_CLOUD_"+billing_dict['user']['USER_NAME']+"_"+today_date+".xlsx"
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=file_name
    )

    
# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
