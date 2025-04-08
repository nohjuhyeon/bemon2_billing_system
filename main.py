from fastapi import FastAPI, Request,HTTPException,Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime, timedelta
from api_func.gov import gov_naver_cloud_api, gov_kt_cloud_api, gov_nhn_cloud_api
from api_func.private import private_kt_cloud_api, private_naver_cloud_api, private_nhn_cloud_api
from databases.connections import Settings
from beanie import PydanticObjectId
import datetime


app = FastAPI()

settings = Settings()
@app.on_event("startup")
async def init_db():
    await settings.initialize_database()
    
from databases.connections import Database

from models.user_list import User_list # 컬랙션을 연결하고, 컬렉션에 저장/불러오기 하는 방법 
collection_user_list = Database(User_list)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# 정렬 기준: bill_month을 연도-월 형식으로 변환
def parse_bill_month(bill_month):
    return datetime.strptime(bill_month, "%Y년 %m월")

def format_currency(value):
    """금액을 1000 단위로 쉼표를 추가하고 '원'을 붙임"""
    return f"{int(value):,} 원"


def api_select(cloud_info):
    if cloud_info['cloud_name'] == 'NAVER':
        if cloud_info['cloud_class'] == '공공':
            return gov_naver_cloud_api
        else:
            return private_naver_cloud_api
    if cloud_info['cloud_name'] == 'KT':
        if cloud_info['cloud_class'] == '공공':
            return gov_kt_cloud_api
        else:
            return private_kt_cloud_api
    if cloud_info['cloud_name'] == 'NHN':
        if cloud_info['cloud_class'] == '공공':
            return gov_nhn_cloud_api
        else:
            return private_nhn_cloud_api

# Load JSON data
def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Routes
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """메인 페이지"""
    # Load user data from JSON
    user_data = load_json("member_list/member_info.json")
    for i in user_data:
        i['cloud_id']= [j['cloud_id'] for j in i['cloud_list']]
        i['cloud_name']= [j['cloud_name'] for j in i['cloud_list']]
        i['cloud_class']= [j['cloud_class'] for j in i['cloud_list']]
    return templates.TemplateResponse("main.html", {"request": request, "users": user_data})

@app.get("/user_info/{user_id}", response_class=HTMLResponse)
async def user_info(
    request: Request,
    user_id: str,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None)     # 종료 날짜 (YYYY-MM 형식)
):
    """고객 정보 페이지"""
    user_data = load_json("member_list/member_info.json")
    user_detail = next((user for user in user_data if user["user_id"] == user_id), None)
    user_detail['cloud_id']= [j['cloud_id'] for j in user_detail['cloud_list']]
    user_detail['cloud_name']= [j['cloud_name'] for j in user_detail['cloud_list']]
    user_detail['cloud_class']= [j['cloud_class'] for j in user_detail['cloud_list']]


    if not user_detail:
        return templates.TemplateResponse("error.html", {"request": request, "message": f"User with ID {user_id} not found."})

    # 오늘 날짜 계산
    today = datetime.today()
    today_str = today.strftime("%Y-%m")

    # 조회 기간 검증
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        if end_date > today_str:
            raise HTTPException(status_code=400, detail="조회 종료 날짜는 오늘 날짜 이후일 수 없습니다.")

    # 기본 조회 기간 설정
    if not start_date or not end_date:
        one_year_ago = today - timedelta(days=365)
        start_date = one_year_ago.strftime("%Y-%m")  # 1년 전
        end_date = today.strftime("%Y-%m")          # 오늘
    data_range = {"start_date": start_date, "end_date": end_date}
    # 예시: 청구 내역 추가
    total_charge_list = []
    for cloud_info in user_detail['cloud_list']:
        cloud_id = cloud_info['cloud_id']
        api_selector = api_select(cloud_info)
        if int(cloud_info['start_date'].replace('-','')) > int(start_date.replace('-','')):
            start_date = cloud_info['start_date']
        if cloud_info['cloud_name'] == 'NAVER':
            start_date = start_date.replace('-','')
            end_date = end_date.replace('-','')
        charge_info_list = api_selector.total_charge_info(start_date,end_date,[cloud_id])
        for charge_info in charge_info_list:
            charge_info['user_name'] = user_detail['user_name']
            charge_info['cloud_name'] = cloud_info['cloud_name']
            charge_info['cloud_class'] = cloud_info['cloud_class']
            charge_info['bill_month_str'] = charge_info['bill_month'][:4] + '년 ' + charge_info['bill_month'][4:] + '월' 
            charge_info['use_amt_str'] = format_currency(charge_info['use_amt'])
            charge_info['total_discount_amt_str'] = format_currency(charge_info['total_discount_amt'])
            charge_info['pay_amt_str'] = format_currency(charge_info['pay_amt'])
        total_charge_list.extend(charge_info_list)
        pass

    sorted_charge_list = sorted(total_charge_list, key=lambda x: parse_bill_month(x['bill_month_str']), reverse=True)

    # 조회 기간을 템플릿에 전달
    return templates.TemplateResponse("user_info.html", {
        "request": request,
        "user": user_detail,
        "billing_history": sorted_charge_list,
        "date_range": data_range
    })


@app.get("/billing_list", response_class=HTMLResponse)
async def billing_list(request: Request):
    """청구 목록 페이지"""
    return templates.TemplateResponse("billing_list.html", {"request": request})

@app.get("/billing_info", response_class=HTMLResponse)
async def billing_info(request: Request):
    """청구 상세 정보 페이지"""
    return templates.TemplateResponse("billing_info.html", {"request": request})

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)