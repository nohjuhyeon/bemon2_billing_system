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
from databases.connections import Database
from models.user_list import User_list
from models.cloud_list import Cloud_list
from models.service_charge_list import Service_charge_list
from models.total_charge import Total_charge

app = FastAPI()

settings = Settings()


@app.on_event("startup")
async def init_db():
    await settings.initialize_database()


collection_user_list = Database(User_list)
collection_cloud_list = Database(Cloud_list)
collection_total_charge = Database(Total_charge)
collection_service_charge = Database(Service_charge_list)
# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


# 정렬 기준: bill_month을 연도-월 형식으로 변환
def parse_bill_month(bill_month):
    return datetime.strptime(bill_month, "%Y년 %m월")


def format_currency(value):
    """금액을 1000 단위로 쉼표를 추가하고 '원'을 붙임"""
    return f"{int(value):,} 원"


def api_select(cloud_info):
    if cloud_info["cloud_name"] == "NAVER":
        if cloud_info["cloud_class"] == "공공":
            return gov_naver_cloud_api
        else:
            return private_naver_cloud_api
    if cloud_info["cloud_name"] == "KT":
        if cloud_info["cloud_class"] == "공공":
            return gov_kt_cloud_api
        else:
            return private_kt_cloud_api
    if cloud_info["cloud_name"] == "NHN":
        if cloud_info["cloud_class"] == "공공":
            return gov_nhn_cloud_api
        else:
            return private_nhn_cloud_api


def generate_month_range(start_date, end_date):
    # 문자열을 datetime 객체로 변환
    start = datetime.strptime(str(start_date), "%Y%m")
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


# Load JSON data
def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def user_dict_create(user_list):
    user_list = [dict(i) for i in user_list]
    for i in user_list:
        i["cloud_id"] = [j["cloud_id"] for j in i["cloud_list"]]
        i["cloud_name"] = [j["cloud_name"] for j in i["cloud_list"]]
        i["cloud_class"] = [j["cloud_class"] for j in i["cloud_list"]]
    return user_list

def period_check(start_date,end_date, today_date):
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

def charge_info_str(total_charge_info):
    total_charge_info["bill_month_str"] = (
        str(total_charge_info["bill_month"])[:4]
        + "년 "
        + str(total_charge_info["bill_month"])[4:]
        + "월"
    )
    total_charge_info["pay_amt_str"] = format_currency(total_charge_info["pay_amt"])
    total_charge_info["total_discount_amt_str"] = format_currency(total_charge_info["total_discount_amt"])
    total_charge_info["use_amt_str"] = format_currency(total_charge_info["use_amt"])
    return total_charge_info


async def user_dict_crate(charge_id,cloud_id_class_dict):
    user_id = charge_id.split("-")[0]
    cloud_name = charge_id.split("-")[1]
    cloud_class = cloud_id_class_dict[charge_id.split("-")[2]]
    bill_month = charge_id.split("-")[3]
    cloud_id = user_id + "-" + cloud_name
    conditions = {"cloud_id": {"$regex": cloud_id}}
    cloud_list = await collection_cloud_list.getsbyconditions(conditions)
    user_dict = dict(cloud_list[0])
    user_dict['bill_month'] = bill_month
    return user_dict


# Routes
@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    """메인 페이지"""
    # # Load user data from JSON
    user_data = await collection_user_list.get_all()
    user_list = user_dict_create(user_data)
    return templates.TemplateResponse(
        "main.html", {"request": request, "users": user_list}
    )


@app.get("/user_info/{user_id}", response_class=HTMLResponse)
async def user_info(
    request: Request,
    user_id: str,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None),  # 종료 날짜 (YYYY-MM 형식)
):
    cloud_name_class_dict = {"공공": "G", "민간": "P", "금융": "F"}
    cloud_id_class_dict = {"G": "공공", "P": "민간", "F": "금융"}
    conditions = {"user_id": {"$regex": user_id}}
    cloud_list = await collection_cloud_list.getsbyconditions(conditions)
    cloud_list = [dict(i) for i in cloud_list]

    if not cloud_list or len(cloud_list) == 0:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": f"User with ID {user_id} not found."},
        )
    else:
        user_detail = {
            "user_id": cloud_list[0]["user_id"],
            "user_name": cloud_list[0]["user_name"],
            "cloud_class": [i["cloud_class"] for i in cloud_list],
            "cloud_name": [i["cloud_name"] for i in cloud_list],
        }

    # 오늘 날짜 계산
    today = datetime.today()
    today_date = int(today.strftime("%Y%m"))

    # 조회 기간 검증
    start_date, end_date = period_check(start_date, end_date,today_date)
    data_range = {"start_date": start_date, "end_date": end_date}
    # 예시: 청구 내역 추가

    conditions = {
        "user_id": {"$regex": user_id},
        "bill_month": {"$gte": start_date, "$lte": end_date},
    }
    total_charge_list = await collection_total_charge.getsbyconditions(conditions)
    if total_charge_list is False:
        total_charge_list = []
    else:
        total_charge_list = [dict(i) for i in total_charge_list]

    mongodb_total_charge_list = [
        {"cloud_key": i["cloud_key"], "bill_month": i["bill_month"]}
        for i in total_charge_list
    ]

    for cloud_info in cloud_list:
        cloud_id = cloud_info["cloud_id"]
        cloud_key = cloud_info["cloud_key"]
        if cloud_info["start_date"] > start_date:
            start_date = cloud_info["start_date"]
        period_list = generate_month_range(start_date, end_date)
        cloud_period_list = [
            {"cloud_key": cloud_key, "bill_month": period_element}
            for period_element in period_list
        ]
        api_selector = api_select(cloud_info)
        for cloud_period_element in cloud_period_list:
            if cloud_period_element not in mongodb_total_charge_list:
                charge_info_list = api_selector.total_charge_info(
                    cloud_key,
                    cloud_period_element["bill_month"],
                    cloud_period_element["bill_month"],
                )
                for charge_info_element in charge_info_list:
                    charge_info_element["user_id"] = user_id
                    charge_info_element["charge_id"] = "-".join(
                        [
                            user_id,
                            cloud_info["cloud_name"],
                            cloud_name_class_dict[cloud_info["cloud_class"]],
                            str(charge_info_element["bill_month"]),
                        ]
                    )
                    if cloud_period_element["bill_month"] != today_date:
                        await collection_total_charge.save(
                            Total_charge(**charge_info_element)
                        )
                    total_charge_list.append(charge_info_element)

        for charge_info in total_charge_list:
            charge_info["user_name"] = user_detail["user_name"]
            charge_info["cloud_name"] = cloud_info["cloud_name"]
            charge_info["cloud_class"] = cloud_info["cloud_class"]
            charge_info = charge_info_str(charge_info)
        pass

    sorted_charge_list = sorted(
        total_charge_list,
        key=lambda x: x["bill_month"],
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
async def billing_list(request: Request):
    """청구 목록 페이지"""
    return templates.TemplateResponse("billing_list.html", {"request": request})


@app.get("/billing_info/{charge_id}", response_class=HTMLResponse)
async def billing_info(
    request: Request,
    charge_id: str,
    start_date: str = Query(None),  # 시작 날짜 (YYYY-MM 형식)
    end_date: str = Query(None),  # 종료 날짜 (YYYY-MM 형식)
):
    """청구 상세 정보 페이지"""
    cloud_name_class_dict = {"공공": "G", "민간": "P", "금융": "F"}
    cloud_id_class_dict = {"G": "공공", "P": "민간", "F": "금융"}

    conditions = {"charge_id": {"$regex": charge_id}}
    total_charge_list = await collection_total_charge.getsbyconditions(conditions)
    user_dict = await user_dict_crate(charge_id,cloud_id_class_dict)
    if total_charge_list is False:
        api_selector = api_select(
            {"cloud_name": user_dict['cloud_name'], "cloud_class": user_dict['cloud_class']}
        )
        total_charge_list = api_selector.total_charge_info(
            user_dict["cloud_key"], user_dict['bill_month'], user_dict['bill_month']
        )
    else:
        total_charge_list = [dict(i) for i in total_charge_list]
    total_charge_info = total_charge_list[0]
    total_charge_info = charge_info_str(total_charge_info)

    conditions = {"charge_id": {"$regex": charge_id}}
    service_charge_list = await collection_service_charge.getsbyconditions(conditions)
    if service_charge_list is False:
        api_selector = api_select(
            {"cloud_name": user_dict['cloud_name'], "cloud_class": user_dict['cloud_class']}
        )
        service_charge_list = api_selector.service_charge_list(
            user_dict["cloud_key"], user_dict['bill_month'], user_dict['bill_month']
        )
    else:
        service_charge_list = [dict(i) for i in service_charge_list]


    for service_charge_info in service_charge_list:
        service_list = service_charge_info['service_list']      
        type_list = []
        service_length = 1
        for service_element in service_list:
            type_elements = [i['type'] for i in type_list]
            if service_element['type'] not in type_elements:
                type_list.append({'type':service_element['type'],'total_use_amt':service_element['use_amt'],'type_list':[{'name':service_element['name'],'use_amt':service_element['use_amt'], 'use_amt_str': format_currency(service_element["use_amt"])}]})
            else:
                type_list[type_elements.index(service_element['type'])]['total_use_amt'] += service_element['use_amt']
                type_list[type_elements.index(service_element['type'])]['type_list'].append({'name':service_element['name'],'use_amt':service_element['use_amt'], 'use_amt_str': format_currency(service_element["use_amt"])})
        for type_element in type_list:
            type_element['total_use_amt_str'] = format_currency(type_element["total_use_amt"])
            type_length = len(type_element['type_list']) + 1
            type_element['type_length'] = type_length
            service_length += type_length
        service_charge_info['service_list'] = type_list
        service_charge_info['service_length'] = service_length
        service_charge_info = charge_info_str(service_charge_info)


    pass
    return templates.TemplateResponse(
        "billing_info.html",
        {"request": request, "user": user_dict, "total_charge_info": total_charge_info, "service_charge_list":service_charge_list},
    )


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
