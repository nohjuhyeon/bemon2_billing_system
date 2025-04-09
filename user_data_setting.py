from api_func.gov import gov_kt_cloud_api, gov_naver_cloud_api, gov_nhn_cloud_api
from api_func.private import private_kt_cloud_api, private_naver_cloud_api, private_nhn_cloud_api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from pymongo import MongoClient
import json
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


last_month = datetime.today() - relativedelta(months=1)
end_date = last_month.strftime("%Y-%m")



mongo_client = MongoClient('mongodb://bemon2_mongodb:27017/mydb?directConnection=true')
# database 연결
database = mongo_client['bemon2']
# collection 작업
collection = database['user_list']

collection.delete_many({})


user_list = load_json("member_list/member_info.json")
for user_dict in user_list:
    collection.insert_one(user_dict)


results = collection.find({},{'_id':0})
user_list = [i for i in results]

collection = database['service_list']
results = collection.find({},{'_id':0})
service_list = [i for i in results]

collection = database['total_charge_list']
results = collection.find({},{'_id':0})
total_charge_list = [i for i in results]

collection = database['service_charge_list']
results = collection.find({},{'_id':0})
service_charge_list = [i for i in results]
pass

collection = database['service_list']
collection.delete_many({})
collection = database['total_charge_list']
collection.delete_many({})
collection = database['service_charge_list']
collection.delete_many({})

for user_element in user_list:
    for cloud_element in user_element['cloud_list']:
        cloud_api = api_select(cloud_element)
        if cloud_element['cloud_name'] == 'NAVER':
            start_date = cloud_element['start_date'].replace('-','')
            end_date = end_date.replace('-','')
        else:
            start_date = cloud_element['start_date']

        collection = database['service_list']
        if cloud_element['cloud_name'] == 'NAVER':
            service_list = {'user_id':user_element['user_id'],'service_list':cloud_api.service_list(cloud_element['cloud_id'],end_date)}
        else:
            service_list = {'user_id':user_element['user_id'],'service_list':cloud_api.service_list(cloud_element['cloud_id'])}
        collection.insert_one(service_list)

        collection = database['total_charge_list']        
        total_charge_list = cloud_api.total_charge_info(cloud_element['cloud_id'],start_date,end_date)
        for total_charge_element in total_charge_list:
            total_charge_element['user_id'] = user_element['user_id']
            collection.insert_one(total_charge_element)

        collection = database['service_charge_list']        
        service_charge_list = cloud_api.service_charge_list(cloud_element['cloud_id'],start_date,end_date)
        for service_charge_element in service_charge_list:
            service_charge_element['user_id'] = user_element['user_id']
            collection.insert_one(service_charge_element)

        pass
pass