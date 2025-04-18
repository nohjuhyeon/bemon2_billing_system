import time
import hmac
import hashlib
import base64
import requests
import xml.etree.ElementTree as ET
import os 
import json 
import pandas as pd

def call_api(command_uri,params_list):
    # API URL 및 쿼리 파라미터
    current_timestamp = str(int(time.time() * 1000))
    access_key = os.environ.get("NAVER_CLOUD_GOV_API_KEY")
    secret_key = os.environ.get("NAVER_CLOUD_GOV_SECRET_KEY")

    base_url = "https://billingapi.apigw.gov-ntruss.com"
    query_params = {
        "responseFormatType":"json"
    }
    for i in params_list.keys():
        query_params[i] = params_list[i]
 
    # 쿼리 파라미터를 포함한 URL 생성
    full_url = f"{base_url}{command_uri}"
    response_url = requests.Request('GET', full_url, params=query_params).prepare().url
    signature_uri = response_url.replace(base_url,'')
    # 헤더 설정
    headers = {
        "x-ncp-apigw-timestamp": current_timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": make_signature(signature_uri, current_timestamp, access_key, secret_key)
    }

    # GET 요청 보내기
    response = requests.get(full_url, headers=headers, params=query_params)
    # 응답 결과 출력
    if response.status_code == 200:
                # JSON 문자열을 딕셔너리로 변환
        json_data = json.loads(response.text)
        return json_data
    else:
        print("Error occurred while calling the API.")
        return None

def make_signature(signature_uri,current_timestamp, access_key, secret_key):
    secret_key = bytes(secret_key, 'UTF-8')

    method = "GET"

    message = method + " " + signature_uri + "\n" + current_timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey


command_uri = "/billing/v1/cost/getCostRelationCodeList"
params_list = {}

# API 호출 및 결과 처리
data_dict = call_api(command_uri,params_list)
naver_member_list = []
category_dict = {}
for data_element in data_dict['getCostRelationCodeListResponse']['costRelationCodeList']:
    category_dict[data_element['contractType']['codeName']] = data_element['productCategory']
def save_dict_to_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"데이터가 {file_path}에 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

# 사용 예시
save_dict_to_json(data_dict, 'data.json')
