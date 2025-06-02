import time
import hmac
import hashlib
import base64
import requests
import xml.etree.ElementTree as ET
import os
import json
import pandas as pd
from datetime import datetime


# Signature 생성 함수
def make_signature(signature_uri, current_timestamp, access_key, secret_key):
    secret_key = bytes(secret_key, "UTF-8")

    method = "GET"

    message = (
        method + " " + signature_uri + "\n" + current_timestamp + "\n" + access_key
    )
    message = bytes(message, "UTF-8")
    signingKey = base64.b64encode(
        hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
    )
    return signingKey


# API 호출 함수
def call_api(command_uri, params_list):
    # API URL 및 쿼리 파라미터
    current_timestamp = str(int(time.time() * 1000))
    access_key = os.environ.get("NAVER_CLOUD_GOV_API_KEY")
    secret_key = os.environ.get("NAVER_CLOUD_GOV_SECRET_KEY")

    base_url = "https://billingapi.apigw.gov-ntruss.com"
    query_params = {"responseFormatType": "json"}
    for i in params_list.keys():
        query_params[i] = params_list[i]

    # 쿼리 파라미터를 포함한 URL 생성
    full_url = f"{base_url}{command_uri}"
    response_url = requests.Request("GET", full_url, params=query_params).prepare().url
    signature_uri = response_url.replace(base_url, "")
    # 헤더 설정
    headers = {
        "x-ncp-apigw-timestamp": current_timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": make_signature(
            signature_uri, current_timestamp, access_key, secret_key
        ),
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


def member_list(startMonth, endMonth):
    command_uri = "/billing/v1/cost/getPartnerDemandCostList"
    params_list = {"startMonth": startMonth, "endMonth": endMonth}

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri, params_list)
    naver_member_list = []
    for i in data_dict["getPartnerDemandCostListResponse"]["partnerDemandCostList"]:
        naver_member_list.append({"cloud_key": i["memberNo"]})
    return naver_member_list


def service_list(memberNoList, contractMonth):
    command_uri = "/billing/v1/cost/getContractSummaryList"
    params_list = {
        "contractMonth": str(contractMonth),
        "isPartner": "true",
        "memberNoList": memberNoList,
    }

    with open("/app/bemon2_billing_system/api_func/contract_product_category.json", "r", encoding="utf-8") as file:
        contract_dict = json.load(file)

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri, params_list)
    naver_service_list = []
    for i in data_dict["getContractSummaryListResponse"]["contractSummaryList"]:
        i["contractTypeCode"] = contract_dict[i["contractType"]["codeName"]]
        naver_service_list.append(
            {
                "code_name": i["contractType"]["codeName"],
                "code": i["contractType"]["code"],
            }
        )
    # 결과를 XML 파일로 저장
    return naver_service_list


def total_charge_info(memberNoList, bill_month):
    command_uri = "/billing/v1/cost/getPartnerDemandCostList"
    params_list = {
        "startMonth": str(bill_month),
        "endMonth": str(bill_month),
        "memberNoList": memberNoList,
    }

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri, params_list)
    naver_total_charge_info = []
    for i in data_dict["getPartnerDemandCostListResponse"]["partnerDemandCostList"]:
        total_discount_amt = (
            i["promiseDiscountAmount"]
            + i["promotionDiscountAmount"]
            + i["etcDiscountAmount"]
            + i["memberPromiseDiscountAddAmount"]
            + i["memberPriceDiscountAmount"]
            + i["customerDiscountAmount"]
            + i["productDiscountAmount"]
            + i["creditDiscountAmount"]
            + i["rounddownDiscountAmount"]
            + i["currencyDiscountAmount"]
        )
        naver_total_charge_info.append(
            {
                "cloud_key": i["memberNo"],
                "bill_month": int(i["demandMonth"]),
                "use_amt": i["useAmount"],
                "total_discount_amt": total_discount_amt,
                "coin_use_amt": i["coinUseAmount"],
                "default_amt": i["defaultAmount"],
                "pay_amt": i["currencyPartnerTotalDemandAmount"],
                "vat_amt": i["currencyPartnerTotalDemandVatAmount"],
                "pay_amt_including_vat": i[
                    "currencyPartnerTotalDemandAmountIncludingVat"
                ],
            }
        )
    if len(naver_total_charge_info) == 1:
        return naver_total_charge_info[0]
    else:
        return None


def service_charge_list(memberNoList, bill_month):
    command_uri = "/billing/v1/cost/getContractDemandCostList"
    params_list = {
        "startMonth": str(bill_month),
        "endMonth": str(bill_month),
        "isPartner": "true",
        "memberNoList": memberNoList,
    }

    with open("/app/bemon2_billing_system/api_func/demand_product_category.json", "r", encoding="utf-8") as file:
        demand_product_category = json.load(file)

    # API 호출 및 결과 처리
    data_dict = call_api(command_uri, params_list)
    naver_service_charge_list = []
    for i in data_dict["getContractDemandCostListResponse"]["contractDemandCostList"]:
        total_discount_amt = (
            i["promotionDiscountAmount"]
            + i["etcDiscountAmount"]
            + i["promiseDiscountAmount"]
        )
        try:
            if i["contract"]["instanceName"] == i["demandType"]["codeName"]:
                name = i["demandTypeDetail"]["codeName"]
            else:
                name = i["contract"]["instanceName"]
            naver_service_charge_list.append(
                {
                    "cloud_key": i["memberNo"],
                    "mdcode": demand_product_category[i["demandType"]["codeName"]]["code"],
                    "service": demand_product_category[i["demandType"]["codeName"]]["codeName"],
                    "bill_month": int(i["demandMonth"]),
                    "type": i["demandType"]["codeName"],
                    "name": name,
                    "region": i["regionCode"],
                    "use_amt": i["useAmount"],
                    "total_discount_amt": total_discount_amt,
                    "pay_amt": i["demandAmount"],
                    "contract_start_date": i["contract"]["contractStartDate"],
                    "contract_end_date": i["contract"]["contractEndDate"],
                }
            )

        except:
            naver_service_charge_list.append(
                {
                    "cloud_key": i["memberNo"],
                    "mdcode": i["demandType"]["code"],
                    "service": i["demandType"]["codeName"],
                    "bill_month": int(i["demandMonth"]),
                    "name": i["demandTypeDetail"]["codeName"],
                    "region": i["regionCode"],
                    "use_amt": i["useAmount"],
                    "total_discount_amt": total_discount_amt,
                    "pay_amt": i["demandAmount"],
                    "contract_start_date": "",
                    "contract_end_date": "",
                }
            )
    service_charge_df = pd.DataFrame(naver_service_charge_list)
    unique_df = service_charge_df.groupby(
        [
            "cloud_key",
            "mdcode",
            "service",
            "bill_month",
            "type",
            "name",
            "region",
            "contract_start_date",
            "contract_end_date",
        ],
        as_index=False,
    ).agg({"use_amt": "sum", "total_discount_amt": "sum", "pay_amt": "sum"})
    unique_list = unique_df.to_dict(orient="records")

    type_result_list = []
    service_result_list = []
    for unique_element in unique_list:
        if unique_element['contract_start_date'] == '':
            unique_element['contract_start_date'] = None
        else:
            date_format = '%Y-%m-%dT%H:%M:%S%z'
            unique_element['contract_start_date'] = datetime.strptime(unique_element['contract_start_date'], date_format)

            # 년-월-일 형식으로 변환
            unique_element['contract_start_date'] = unique_element['contract_start_date'].strftime('%Y-%m-%d')


        type_list = [i["type"] for i in type_result_list]
        if unique_element["type"] not in type_list:
            type_result_list.append(
                {
                    "cloud_key": unique_element["cloud_key"],
                    "service_code": unique_element["mdcode"],
                    "service": unique_element["service"],
                    "bill_month": unique_element["bill_month"],
                    "use_amt": unique_element["use_amt"],
                    "total_discount_amt": unique_element["total_discount_amt"],
                    "pay_amt": unique_element["pay_amt"],
                    "type": unique_element["type"],
                    "type_use_amt": unique_element["use_amt"],
                    "type_pay_amt": unique_element["pay_amt"],
                    "type_list": [
                        {
                            "name": unique_element["name"],
                            "region": unique_element["region"],
                            "use_amt": unique_element["use_amt"],
                            "pay_amt": unique_element["pay_amt"],
                            "start_date": unique_element[
                                "contract_start_date"
                            ],
                        }
                    ],
                }
            )
        else:
            list_index = type_list.index(unique_element["type"])
            type_result_list[list_index]["type_use_amt"] += unique_element["use_amt"]
            type_result_list[list_index]["type_pay_amt"] += unique_element["pay_amt"]
            type_result_list[list_index]["type_list"].append(
                {
                    "name": unique_element["name"],
                    "region": unique_element["region"],
                    "use_amt": unique_element["use_amt"],
                    "pay_amt": unique_element["pay_amt"],
                    "start_date": unique_element["contract_start_date"],
                }
            )
    for type_element in type_result_list:
        code_list = [i["service"] for i in service_result_list]
        if type_element["service"] not in code_list:
            service_result_list.append(
                {
                    "cloud_key": type_element["cloud_key"],
                    "service_code": type_element["service_code"],
                    "service": type_element["service"],
                    "bill_month": type_element["bill_month"],
                    "use_amt": type_element["type_use_amt"],
                    "total_discount_amt": type_element["total_discount_amt"],
                    "pay_amt": type_element["pay_amt"],
                    "service_list": [
                        {
                            "type": type_element["type"],
                            "type_use_amt": type_element["type_use_amt"],
                            "type_pay_amt": type_element["type_pay_amt"],
                            "type_list": type_element["type_list"]
                        }
                    ],
                }
            )
        else:
            list_index = code_list.index(type_element["service"])
            service_result_list[list_index]["use_amt"] += type_element["type_use_amt"]
            service_result_list[list_index]["total_discount_amt"] += type_element[
                "total_discount_amt"
            ]
            service_result_list[list_index]["pay_amt"] += type_element["pay_amt"]
            service_result_list[list_index]["service_list"].append(
                {
                            "type": type_element["type"],
                            "type_use_amt": type_element["type_use_amt"],
                            "type_pay_amt": type_element["type_pay_amt"],
                            "type_list": type_element["type_list"]
                }
            )

            
    return service_result_list

# Main 실행
if __name__ == "__main__":
    # Access Key와 Secret Key 설정
    bill_month = 202503
    contractMonth = 202503
    memberNoList = ["10395"]
    member_list(bill_month, bill_month)
    service_list(memberNoList, contractMonth)
    total_charge_info(memberNoList, bill_month)
    service_charge_list(memberNoList, bill_month)
