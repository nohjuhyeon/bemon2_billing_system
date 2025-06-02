import os
import requests
import json
from datetime import datetime, timedelta


class PrivateKTCloudAPI:

    def __init__(self,user_id,bill_month):
        self.reseller_key = os.environ.get("KT_CLOUD_RESELLER_KEY")
        self.user_id = user_id
        self.bill_month = bill_month
    # API 호출 함수
    def call_api(self,command, param_list):

        # API URL 및 쿼리 파라미터
        uri = "https://api.ucloudbiz.olleh.com/reseller/v1/client/api"
        query_params = {"resellerKey": self.reseller_key, "command": command, "response": "json"}
        for i in param_list.keys():
            query_params[i] = param_list[i]

        # GET 요청 보내기
        response = requests.get(uri, params=query_params)
        if response.status_code == 200:
            # JSON 문자열을 딕셔너리로 변환
            json_data = json.loads(response.text)
            return json_data
        else:
            print("Error occurred while calling the API.")
            return None


    def member_list(self):
        command = "memberInfo"
        param_list = {}

        response = self.call_api(command, param_list)
        kt_member_list = []
        for i in response["memberinforesponse"]["memberids"]:
            kt_member_list.append({"cloud_key": i["id"]})
        return kt_member_list


    def service_list(self):
        command = "serviceInfo"
        param_list = {"emailId": self.user_id}

        response = self.call_api(command, param_list)
        kt_service_list = []
        for i in response["serviceinforesponse"]["servicecodes"]:
            kt_service_list.append({"code_name": i["code_nm"], "code": i["code"]})
        return kt_service_list


    def total_charge_info(self):
        bill_month = datetime.strptime(str(self.bill_month), "%Y%m")
        bill_month = bill_month.strftime("%Y-%m")  

        command = "listCharges"
        param_list = {
            "type": "billingInfoListAccounts",
            "emailId": self.user_id,
            "startDate": bill_month,
            "endDate": bill_month,
        }

        response = self.call_api(command, param_list)
        kt_total_charge_info = []
        if response:
            for i in response["billinginfolistaccountsresponse"]["chargeaccountlists"]:
                if self.user_id == i["account"]:
                    kt_total_charge_info.append(
                        {
                            "cloud_key": self.user_id,
                            "bill_month": int(i["bill_month"].replace("-", "")),
                            "use_amt": i["pay_amt"] + i["total_discount_amt"],
                            "total_discount_amt": i["total_discount_amt"],
                            "pay_amt": i["pay_amt"],
                            "coin_use_amt": 0,
                            "default_amt": 0,
                            "vat_amt": 0,
                            "pay_amt_including_vat": i["pay_amt"],
                        }
                    )
        if len(kt_total_charge_info) == 1:
            return kt_total_charge_info[0]
        else:
            return None

    def service_charge_list(self):
        bill_month = datetime.strptime(str(self.bill_month), "%Y%m")
        bill_month = bill_month.strftime("%Y-%m")
        command = "listCharges"
        param_list = {
            "type": "serviceChargeInfoAccount",
            "emailId": self.user_id,
            "startDate": bill_month,
            "endDate": bill_month,
        }

        response = self.call_api(command, param_list)
        kt_service_charge_list = []
        for i in response["servicechargeinfoaccountresponse"]["servicechargeinfo"]:
            mdcode = i["mdcode"]
            type_list = []
            for j in response["servicechargeinfoaccountresponse"]["serverserviceinfo"]:
                if  j["reg_dttm"] == '':
                    j["reg_dttm"] = None
                if j["mdcode"] == mdcode:
                    type_list.append(
                        {
                            "name": j["name"],
                            "type": j["type"],
                            "use_amt": j["pay_amt"],
                            "pay_amt": j["pay_amt"],
                            "region": None,
                            "start_date": j["reg_dttm"],
                        }
                    )
            kt_service_charge_list.append(
                {
                    "cloud_key": self.user_id,
                    "service_code": i["mdcode"],
                    "service": i["service"],
                    "bill_month": int(i["bill_month"].replace("-", "")),
                    "use_amt": i["pay_amt"] + i["total_discount_amt"],
                    "total_discount_amt": i["total_discount_amt"],
                    "pay_amt": i["pay_amt"],
                    "type_list": type_list,
                }
            )
        for kt_service_charge_element in kt_service_charge_list:
            type_list = []
            for type_element in kt_service_charge_element['type_list']:
                type_name_list = [i['type'] for i in type_list]
                if type_element['type'] not in type_name_list:
                    type_dict = {
                            "type": type_element["type"],
                            "type_use_amt": type_element['use_amt'],
                            "type_pay_amt": type_element['pay_amt'],
                            "type_list":[{"name": type_element["name"],"use_amt": type_element["use_amt"],"pay_amt": type_element["pay_amt"],"region": None,"start_date": type_element["start_date"]}]
                            }
                    type_list.append(type_dict)
                else:
                    type_index = type_name_list.index(type_element['type'])
                    type_list[type_index]['type_use_amt'] += type_element['use_amt']
                    type_list[type_index]['type_pay_amt'] += type_element['use_amt']
                    type_list[type_index]['type_list'].append({"name": type_element["name"],"use_amt": type_element["use_amt"],"pay_amt": type_element["pay_amt"],"region": None,"start_date": type_element["start_date"]})
            kt_service_charge_element['service_list'] = type_list
        return kt_service_charge_list

# Main 실행
if __name__ == "__main__":
    # Reseller Key 설정
    user_id = "zinwu@softbowl.co.kr"
    bill_month = 202503
    # API 호출
    private_kt_cloud_api = PrivateKTCloudAPI(user_id,bill_month)
    private_kt_cloud_api.member_list()
    private_kt_cloud_api.service_list()
    private_kt_cloud_api.total_charge_info()
    private_kt_cloud_api.service_charge_list()
