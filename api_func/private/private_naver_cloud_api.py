import time
import hmac
import hashlib
import base64
import requests
import xml.etree.ElementTree as ET
import os 
import json 
import pandas as pd
# Signature 생성 함수
def make_signature(signature_uri,current_timestamp, access_key, secret_key):
    secret_key = bytes(secret_key, 'UTF-8')

    method = "GET"

    message = method + " " + signature_uri + "\n" + current_timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey

# API 호출 함수
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
    print(full_url)
    response_url = requests.Request('GET', full_url, params=query_params).prepare().url
    print("Request URL:", response_url)  # 디버깅용 출력
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
    print("Status Code:", response.status_code)
    if response.status_code == 200:
                # JSON 문자열을 딕셔너리로 변환
        json_data = json.loads(response.text)

        return json_data
    else:
        print("Error occurred while calling the API.")
        return None

def save_json(data, filename):
    """
    JSON 데이터를 파일로 저장합니다.
    :param data: JSON 데이터 (문자열 또는 딕셔너리)
    :param filename: 저장할 파일 이름
    """
    try:
        # 파일로 저장
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"JSON 데이터가 {filename} 파일에 저장되었습니다.")
    except Exception as e:
        print(f"JSON 파일 저장 중 오류 발생: {e}")

def member_list(startMonth,endMonth):
    command_uri = "/billing/v1/cost/getPartnerDemandCostList"
    params_list = {"startMonth": startMonth,"endMonth": endMonth}

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri,params_list)
    naver_member_list = []
    for i in data_dict['getPartnerDemandCostListResponse']['partnerDemandCostList']:
        naver_member_list.append({'cloud_id':i['memberNo']})
    # 결과를 XML 파일로 저장
    save_json(naver_member_list, "member_list/naver_member_list.json")
    return naver_member_list

def service_list(memberNoList,contractMonth):
    command_uri = "/billing/v1/cost/getContractSummaryList"
    params_list = {"contractMonth":contractMonth,"isPartner":"true","memberNoList":memberNoList}

    with open('contract_dict.json', "r", encoding="utf-8") as file:
        contract_dict = json.load(file)

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri,params_list)
    naver_service_list = []
    for i in data_dict['getContractSummaryListResponse']['contractSummaryList']:
        i['contractTypeCode'] = contract_dict[i['contractType']['codeName']]
        naver_service_list.append({'code_name':i['contractType']['codeName'],'code':i['contractType']['code']})
    # 결과를 XML 파일로 저장
    save_json(naver_service_list, "service_list/naver_service_list.json")
    return naver_service_list

def total_charge_info(memberNoList,startMonth,endMonth):
    command_uri = "/billing/v1/cost/getPartnerDemandCostList"
    params_list = {"startMonth": startMonth,"endMonth": endMonth,"memberNoList":memberNoList}

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri,params_list)
    naver_total_charge_info = []
    for i in data_dict['getPartnerDemandCostListResponse']['partnerDemandCostList']:
        total_discount_amt = i['promiseDiscountAmount']+i['promotionDiscountAmount']+i['etcDiscountAmount']+i['memberPromiseDiscountAddAmount']+i['memberPriceDiscountAmount']+i['customerDiscountAmount']+i['productDiscountAmount']+i['creditDiscountAmount']+i['rounddownDiscountAmount']+i['currencyDiscountAmount']
        naver_total_charge_info.append({'cloud_id':i['memberNo'],'bill_month':i['demandMonth'],'use_amt':i['useAmount'],'total_discount_amt':total_discount_amt,'coin_use_amt':i['coinUseAmount'],'default_amt':i['defaultAmount'],'pay_amt':i['currencyPartnerTotalDemandAmount'],'vat_amt':i['currencyPartnerTotalDemandVatAmount'],'pay_amt_including_vat':i['currencyPartnerTotalDemandAmountIncludingVat'],})
    # 결과를 XML 파일로 저장
    save_json(naver_total_charge_info, "total_charge_info/naver_total_charge_info.json")
    return naver_total_charge_info
def service_charge_list(memberNoList,startMonth,endMonth):
    command_uri = "/billing/v1/cost/getContractDemandCostList"
    params_list = {"startMonth": startMonth,"endMonth": endMonth,"isPartner":"true","memberNoList":memberNoList}

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri,params_list)
    # 결과를 XML 파일로 저장
    naver_service_charge_list = []
    for i in data_dict['getContractDemandCostListResponse']['contractDemandCostList']:
        total_discount_amt = i['promotionDiscountAmount']+i['etcDiscountAmount']+i['promiseDiscountAmount']
        try:
            if i['contract']['instanceName'] == i['demandType']['codeName']:
                name = i['demandTypeDetail']['codeName']
            else:
                name = i['contract']['instanceName']
            naver_service_charge_list.append({'mdcode':i['contract']['contractType']['code'],'service':i['contract']['contractType']['codeName'],'name':name,'region':i['regionCode'],'use_amt':i['useAmount'],'total_discount_amt':total_discount_amt,'pay_amt':i['demandAmount'],'contract_start_date':i['contract']['contractStartDate'],'contract_end_date':i['contract']['contractEndDate']})

        except:
            naver_service_charge_list.append({'mdcode':i['demandType']['code'],'service':i['demandType']['codeName'],'name':i['demandTypeDetail']['codeName'],'region':i['regionCode'],'use_amt':i['useAmount'],'total_discount_amt':total_discount_amt,'pay_amt':i['demandAmount'],'contract_start_date':'', 'contract_end_date':''})
    service_charge_df = pd.DataFrame(naver_service_charge_list)
    # mdcode, service, name, region, contract_start_date, contract_end_date가 같은 값들 그룹화 후 use_amt, total_discount_amt, pay_amt 합산
    unique_df = service_charge_df.groupby(
        ['mdcode', 'service', 'name', 'region', 'contract_start_date', 'contract_end_date'],
        as_index=False
    ).agg({
        'use_amt': 'sum',
        'total_discount_amt': 'sum',
        'pay_amt': 'sum'
    })
    unique_list = unique_df.to_dict(orient='records')
    result_list = []
    for unique_element in unique_list:
        code_list = [i['service'] for i in result_list]
        if unique_element['service'] not in code_list:
            result_list.append({'service_code':unique_element['mdcode'],'service':unique_element['service'],'use_amt':unique_element['use_amt'],'total_discount_amt':unique_element['total_discount_amt'],'pay_amt':unique_element['pay_amt'],'service_list':[{'name':unique_element['name'],'region':unique_element['region'],'use_amt':unique_element['use_amt'],'contract_start_date':unique_element['contract_start_date']}]})
        else:
            list_index = code_list.index(unique_element['service'])
            result_list[list_index]['use_amt'] += unique_element['use_amt']
            result_list[list_index]['total_discount_amt'] += unique_element['total_discount_amt']
            result_list[list_index]['pay_amt'] += unique_element['pay_amt']
            result_list[list_index]['service_list'].append({'name':unique_element['name'],'region':unique_element['region'],'use_amt':unique_element['use_amt'],'contract_start_date':unique_element['contract_start_date']})
    save_json(result_list, "service_charge_list/naver_service_charge_list.json")
    return result_list
    
# Main 실행
if __name__ == "__main__":
    # Access Key와 Secret Key 설정
    startMonth="202503"
    endMonth="202503"
    contractMonth="202503"
    memberNoList=["10395"]
    member_list(startMonth,endMonth)
    service_list(memberNoList,contractMonth)
    total_charge_info(startMonth,endMonth,memberNoList)
    service_charge_list(startMonth,endMonth,memberNoList)

