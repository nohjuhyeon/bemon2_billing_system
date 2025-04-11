from api_func.gov import gov_kt_cloud_api, gov_naver_cloud_api, gov_nhn_cloud_api
from api_func.private import (
    private_kt_cloud_api,
    private_naver_cloud_api,
    private_nhn_cloud_api,
)
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from pymongo import MongoClient
import json
import os 


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


# Load JSON data
def load_json(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


from datetime import datetime, timedelta


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


def init_mongo_database():
    mongodb_url = os.environ.get("DATABASE_URL")
    mongo_client = MongoClient(
        mongodb_url
    )
    # database 연결
    database = mongo_client["bemon2"]

    return database




def user_list_insert(database):
    # collection 작업
    user_list = load_json("member_list/member_info.json")
    for user_dict in user_list:
        collection = database['cloud_list']
        for cloud_dict in user_dict['cloud_list']:
            cloud_dict['user_id'] = user_dict['user_id']
            cloud_dict['user_name'] = user_dict['user_name']
            cloud_dict['cloud_id'] = user_dict['user_id'] + '-' + cloud_dict['cloud_name']
            collection.insert_one(cloud_dict)
        collection = database["user_list"]
        collection.insert_one(user_dict)


def service_list_update(database, current_user_list,end_date):

    for user_element in current_user_list:
        for cloud_element in user_element["cloud_list"]:
            cloud_api = api_select(cloud_element)
            collection = database["service_list"]
            results = collection.find({})
            current_service_list = [i for i in results]

            if cloud_element["cloud_name"] == "NAVER":
                service_list = {
                    "cloud_id": cloud_element["cloud_id"],
                    "service_list": cloud_api.service_list(
                        cloud_element["cloud_key"], end_date
                    ),
                }
            else:
                service_list = {
                    "cloud_id": cloud_element["cloud_id"],
                    "service_list": cloud_api.service_list(cloud_element["cloud_key"]),
                }
            if service_list["cloud_id"] not in [
                i["cloud_id"] for i in current_service_list
            ]:
                collection.insert_one(service_list)
            else:
                user_index = [i["cloud_id"] for i in current_service_list].index(
                    service_list["cloud_id"]
                )
                cloud_index = current_service_list[user_index]["_id"]
                if (
                    current_service_list[user_index]["service_list"]
                    != service_list["service_list"]
                ):
                    collection.update_one(
                        {"_id": cloud_index},  # 필터 조건
                        {
                            "$set": {"service_list": service_list["service_list"]}
                        },  # 업데이트 내용
                    )


def total_charge_list_update(database, current_user_list,end_date):
    cloud_class_dict = {'공공':'G','민간':'P','금융':'F'}

    collection = database["total_charge_list"]
    results = collection.find({})
    current_total_charge_list = [
        {"cloud_key": i["cloud_key"], "bill_month": i["bill_month"]} for i in results
    ]

    for user_element in current_user_list:
        for cloud_element in user_element["cloud_list"]:
            cloud_api = api_select(cloud_element)
            period_list = generate_month_range(cloud_element["start_date"], end_date)
            cloud_period_list = [
                {"cloud_key": cloud_element["cloud_key"], "bill_month": period_element}
                for period_element in period_list
            ]

            collection = database["total_charge_list"]
            for cloud_month in cloud_period_list:
                check_month = {
                    "cloud_key": cloud_month["cloud_key"],
                    "bill_month": cloud_month["bill_month"],
                }
                if check_month not in current_total_charge_list:
                    if cloud_element["cloud_name"] == "NAVER":
                        bill_month = cloud_month["bill_month"]
                    else:
                        bill_month = cloud_month["bill_month"]
                    total_charge_list = cloud_api.total_charge_info(
                        cloud_month["cloud_key"], bill_month, bill_month
                    )
                    for total_charge_element in total_charge_list:
                        total_charge_element["user_id"] = user_element["user_id"]
                        total_charge_element['charge_id'] = '-'.join([total_charge_element['user_id'],cloud_element['cloud_name'],cloud_class_dict[cloud_element['cloud_class']],str(total_charge_element['bill_month'])])
                        collection.insert_one(total_charge_element)
                else:
                    pass


def service_charge_list_update(database, current_user_list,end_date):
    cloud_class_dict = {'공공':'G','민간':'P','금융':'F'}

    collection = database["service_charge_list"]
    results = collection.find({})
    current_service_charge_list = [
        {"cloud_key": i["cloud_key"], "bill_month": i["bill_month"]} for i in results
    ]

    for user_element in current_user_list:
        for cloud_element in user_element["cloud_list"]:
            cloud_api = api_select(cloud_element)
            period_list = generate_month_range(cloud_element["start_date"], end_date)
            cloud_period_list = [
                {"cloud_key": cloud_element["cloud_key"], "bill_month": period_element}
                for period_element in period_list
            ]

            collection = database["service_charge_list"]
            for cloud_month in cloud_period_list:
                check_month = {
                    "cloud_key": cloud_month["cloud_key"],
                    "bill_month": cloud_month["bill_month"],
                }
                if check_month not in current_service_charge_list:
                    if cloud_element["cloud_name"] == "NAVER":
                        bill_month = cloud_month["bill_month"]
                    else:
                        bill_month = cloud_month["bill_month"]
                    total_charge_list = cloud_api.service_charge_list(
                        cloud_month["cloud_key"], bill_month, bill_month
                    )
                    for total_charge_element in total_charge_list:
                        total_charge_element["user_id"] = user_element["user_id"]
                        total_charge_element['charge_id'] = '-'.join([total_charge_element['user_id'],cloud_element['cloud_name'],cloud_class_dict[cloud_element['cloud_class']],str(total_charge_element['bill_month'])])
                        collection.insert_one(total_charge_element)
                else:
                    pass


if __name__ == "__main__":

    database = init_mongo_database()
    collection = database["total_charge_list"]
    collection.delete_many({})
    collection = database["cloud_list"]
    collection.delete_many({})
    collection = database["service_list"]
    collection.delete_many({})
    collection = database["user_list"]
    collection.delete_many({})
    collection = database["service_charge_list"]
    collection.delete_many({})
    user_list_insert(database)

    collection = database["user_list"]
    results = collection.find({})
    current_user_list = [i for i in results]
    last_month = datetime.today() - relativedelta(months=1)
    end_date = int(last_month.strftime("%Y%m"))

    service_list_update(database, current_user_list,end_date)
    total_charge_list_update(database, current_user_list,end_date)
    service_charge_list_update(database, current_user_list,end_date)
