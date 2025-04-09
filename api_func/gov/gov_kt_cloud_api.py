import os
import requests
import json
# API 호출 함수
def call_api(command,param_list):
    reseller_key = os.environ.get("KT_CLOUD_RESELLER_KEY")

    # API URL 및 쿼리 파라미터
    uri = 'https://api.ucloudbiz.olleh.com/reseller/v1/client/api'
    query_params = {
        "resellerKey": reseller_key,
        "command": command,
        "response":"json"
    }
    for i in param_list.keys():
        query_params[i] = param_list[i]
        
    # GET 요청 보내기
    response = requests.get(uri, params=query_params)
    response_url = requests.Request('GET', uri, params=query_params).prepare().url
    print("Request URL:", response_url)  # 디버깅용 출력

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


def member_list():
    command = "memberInfo"
    param_list = {}

    response = call_api(command,param_list)
    kt_member_list = []
    for i in response['memberinforesponse']['memberids']:
        kt_member_list.append({'cloud_id':i['id']})
    save_json(kt_member_list,"member_list/kt_member_list.json")
    return kt_member_list

def service_list(user_id):
    command = "serviceInfo"
    param_list = {'emailId':user_id}

    response = call_api(command,param_list)
    kt_service_list = []
    for i in response['serviceinforesponse']['servicecodes']:
        kt_service_list.append({'code_name':i['code_nm'],'code':i['code']})
    save_json(kt_service_list,"service_list/kt_service_list.json")
    return kt_service_list

def total_charge_info(user_id,start_date,end_date):
    command = "listCharges"
    param_list = {'type':'billingInfoListAccounts','emailId':user_id,'startDate':start_date,'endDate':end_date}

    response = call_api(command,param_list)
    kt_total_charge_info = []
    for i in response['billinginfolistaccountsresponse']['chargeaccountlists']:
        kt_total_charge_info.append({'cloud_id':i['account'],'bill_month':i['bill_month'].replace('-',''),'use_amt':i['pay_amt']+i['total_discount_amt'],'total_discount_amt':i['total_discount_amt'],'pay_amt':i['pay_amt']})
    save_json(kt_total_charge_info,"total_charge_info/kt_total_charge_info.json")
    return kt_total_charge_info

def service_charge_list(user_id,start_date,end_date):
    command = "listCharges"
    param_list = {'type':'serviceChargeInfoAccount','emailId':user_id,'startDate':start_date,'endDate':end_date}

    response = call_api(command,param_list)
    kt_service_charge_list = []
    for i in response['servicechargeinfoaccountresponse']['servicechargeinfo']:
        mdcode = i['mdcode']
        service_list = []
        for j in response['servicechargeinfoaccountresponse']['serverserviceinfo']:
            if j['mdcode'] == mdcode:
                service_list.append({'name':j['name'],'type':j['type'],'use_amt':j['pay_amt'],'reg_dttm':j['reg_dttm']})
        i['service_list'] = service_list
        kt_service_charge_list.append({'service_code':i['mdcode'],'service':i['service'],'bill_month':i['bill_month'],'use_amt':i['pay_amt']+i['total_discount_amt'],'total_dicount_amt':i['total_discount_amt'],'pay_amt':i['pay_amt'],'service_list':service_list})
    save_json(kt_service_charge_list,"service_charge_list/kt_service_charge_list.json")
    return kt_service_charge_list



# Main 실행
if __name__ == "__main__":
    # Reseller Key 설정
    user_id = 'zinwu@softbowl.co.kr'
    start_date = '2025-01'
    end_date = '2025-03'
    # API 호출
    member_list()
    service_list(user_id)
    total_charge_info(user_id,start_date,end_date)
    service_charge_list(user_id,start_date,end_date)
# memberInfo
    # command = "memberInfo"
    # param_list = {}

# serviceInfo
    # command = "serviceInfo"
    # param_list = {'emailId':'zinwu@softbowl.co.kr'}

# listCharges
    # command = "listCharges"
    # param_list = {'type':'billingInfoListAccounts','emailId':'zinwu@softbowl.co.kr','startDate':'202503','endDate':'202503'}

