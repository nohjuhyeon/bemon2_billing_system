from datetime import datetime
import os
import requests
import json
import pandas as pd

class KtCloudApi:
    """
    KT 클라우드 API를 호출하여 사용자, 서비스, 청구 데이터를 조회하고 처리하는 기능을 제공하는 클래스.

    Attributes:
        base_url (str): KT 클라우드 API의 기본 URL.
        reseller_key (str): API 호출을 위한 Reseller Key.

    주요 기능:
        1. API 호출(call_api): 특정 명령과 파라미터를 사용하여 API를 호출.
        2. 회원 목록 조회(member_list): 클라우드 사용자 목록을 가져옴.
        3. 서비스 목록 조회(service_list): 특정 사용자의 서비스 정보를 가져옴.
        4. 총 사용 요금 정보 조회(total_charge_info): 특정 사용자의 총 청구 정보를 조회.
        5. 서비스별 비용 정보 조회(service_charge_list): 서비스별, 타입별 및 아이템별 비용 정보를 조회.
    """

    def __init__(self, api_type):
        """
        KtCloudApi 클래스의 초기화 메서드.

        Args:
            api_type (str): API 타입 ('공공' 또는 '민간').

        주요 작업:
            1. API 타입에 따라 기본 URL과 Reseller Key를 설정.
            2. 환경 변수에서 Reseller Key를 가져옴.
        """
        if api_type == '공공':
            self.base_url = "https://api.ucloudbiz.olleh.com/greseller/v1/client/api"
            self.reseller_key = os.environ.get("KT_CLOUD_GOV_RESELLER_KEY")
        elif api_type == '민간':
            self.base_url = "https://api.ucloudbiz.olleh.com/reseller/v1/client/api"
            self.reseller_key = os.environ.get("KT_CLOUD_PRIV_RESELLER_KEY")

    def call_api(self, command, param_list):
        """
        KT 클라우드 API를 호출하는 메서드.

        Args:
            command (str): API 명령어.
            param_list (dict): API 호출에 필요한 파라미터.

        Returns:
            dict: API 응답 데이터를 담은 딕셔너리. HTTP 요청이 실패하면 None 반환.

        Variables:
            query_params (dict): API 호출을 위한 쿼리 파라미터.
            response (requests.Response): HTTP 응답 객체.

        주요 작업:
            1. API 호출 URL과 파라미터를 설정.
            2. GET 요청을 보내고 응답 데이터를 JSON 형식으로 변환.
            3. HTTP 요청 실패 시 오류 메시지를 출력.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 처리.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 처리.
            - requests.exceptions.RequestException: HTTP 요청 중 발생하는 오류를 처리.
            - json.JSONDecodeError: 응답 데이터 파싱 중 발생하는 오류를 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력.

        """
        try:
            query_params = {"resellerKey": self.reseller_key, "command": command, "response": "json"}
            for param_element in param_list.keys():
                query_params[param_element] = param_list[param_element]

            response = requests.get(self.base_url, params=query_params)
            if response.status_code == 200:
                json_data = json.loads(response.text)
                return json_data
            else:
                raise ("API 호출 중 오류가 발생하였습니다.")
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e:
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except requests.exceptions.RequestException as e:
            raise (f"HTTP 요청 중 오류가 발생하였습니다: {e}")
        except json.JSONDecodeError as e:
            raise (f"응답 데이터 파싱 중 오류가 발생하였습니다: {e}")
        except Exception as e:
            raise (f"API 호출 중 알 수 없는 오류가 발생하였습니다: {e}")

    def member_list(self):
        """
        KT 클라우드 사용자 목록을 조회하는 메서드.

        Returns:
            list: 사용자 목록을 담은 딕셔너리 리스트.

        Variables:
            command (str): API 명령어.
            param_list (dict): API 호출 파라미터.
            response (dict): API 응답 데이터.
            kt_member_list (list): 사용자 목록을 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 사용자 목록을 조회.
            2. 응답 데이터를 파싱하여 사용자 ID를 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command = "memberInfo"
            param_list = {}

            response = self.call_api(command, param_list)
            kt_member_list = []
            for i in response["memberinforesponse"]["memberids"]:
                kt_member_list.append({"cloud_key": i["id"]})
            return kt_member_list
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"사용자 목록 조회 중 알 수 없는 오류가 발생하였습니다: {e}")

    def service_list(self, user_id):
        """
        특정 사용자의 서비스 정보를 조회하는 메서드.

        Args:
            user_id (str): 사용자의 이메일 ID.

        Returns:
            list: 사용자 서비스 정보를 담은 딕셔너리 리스트.

        Variables:
            command (str): API 명령어.
            param_list (dict): API 호출 파라미터.
            response (dict): API 응답 데이터.
            kt_service_list (list): 서비스 정보를 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 특정 사용자의 서비스 정보를 조회.
            2. 응답 데이터를 파싱하여 서비스 코드와 이름을 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command = "serviceInfo"
            param_list = {"emailId": user_id}

            response = self.call_api(command, param_list)
            kt_service_list = []
            for i in response["serviceinforesponse"]["servicecodes"]:
                kt_service_list.append({"code_name": i["code_nm"], "code": i["code"]})
            return kt_service_list
        
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"서비스 목록 조회 중 알 수 없는 오류가 발생하였습니다: {e}")

    def total_charge_info(self, user_id, bill_month):
        """
        특정 사용자의 총 청구 정보를 조회하는 메서드.

        Args:
            user_id (str): 사용자의 이메일 ID.
            bill_month (int): 청구 월 (YYYYMM 형식).

        Returns:
            dict: 총 청구 정보를 담은 딕셔너리. 데이터가 없으면 None 반환.

        Variables:
            command (str): API 명령어.
            param_list (dict): API 호출 파라미터.
            response (dict): API 응답 데이터.
            kt_total_charge_info (list): 총 청구 정보를 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 특정 사용자의 총 청구 정보를 조회.
            2. 응답 데이터에서 필요한 정보를 파싱하여 반환.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 처리.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            bill_month = datetime.strptime(str(bill_month), "%Y%m")
            bill_month = bill_month.strftime("%Y-%m")

            command = "listCharges"
            param_list = {
                "type": "billingInfoListAccounts",
                "emailId": user_id,
                "startDate": bill_month,
                "endDate": bill_month,
            }

            response = self.call_api(command, param_list)
            kt_total_charge_info = []
            if response:
                for i in response["billinginfolistaccountsresponse"]["chargeaccountlists"]:
                    if user_id == i["account"]:
                        kt_total_charge_info.append(
                            {
                                "cloud_key": user_id,
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
                raise ("총 청구 정보가 여러 개이거나 존재하지 않습니다.")
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"총 청구 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")
        
    def service_charge_list(self, user_id, bill_month):
        """
        특정 사용자의 서비스별, 타입별, 아이템별 비용 정보를 조회하는 메서드.

        Args:
            user_id (str): 사용자의 이메일 ID.
            bill_month (int): 청구 월 (YYYYMM 형식).

        Returns:
            tuple: 서비스별, 타입별, 아이템별 비용 정보를 담은 리스트.

        Variables:
            command (str): API 명령어.
            param_list (dict): API 호출 파라미터.
            response (dict): API 응답 데이터.
            kt_service_charge_list (list): 서비스별 비용 정보를 저장하는 리스트.
            kt_type_charge_list (list): 타입별 비용 정보를 저장하는 리스트.
            kt_item_charge_list (list): 아이템별 비용 정보를 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 서비스별 비용 정보를 조회.
            2. 응답 데이터를 파싱하여 서비스별, 타입별, 아이템별 비용 정보를 정리.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            bill_month = datetime.strptime(str(bill_month), "%Y%m")
            bill_month = bill_month.strftime("%Y-%m")
            command = "listCharges"
            param_list = {
                "type": "serviceChargeInfoAccount",
                "emailId": user_id,
                "startDate": bill_month,
                "endDate": bill_month,
            }
            response = self.call_api(command, param_list)

            if response:
                kt_service_charge_list = []
                for service_charge_info in response["servicechargeinfoaccountresponse"]["servicechargeinfo"]:
                    service_dict = {
                        "cloud_key": user_id,
                        "service_code": service_charge_info["mdcode"],
                        "service": service_charge_info["service"],
                        "bill_month": int(service_charge_info["bill_month"].replace("-", "")),
                        "use_amt": service_charge_info["pay_amt"] + service_charge_info["total_discount_amt"],
                        "total_discount_amt": service_charge_info["total_discount_amt"],
                        "pay_amt": service_charge_info["pay_amt"]
                        }
                    kt_service_charge_list.append(service_dict)

                kt_item_charge_list = []
                for item_info in response["servicechargeinfoaccountresponse"]["serverserviceinfo"]:
                    start_date = item_info['reg_dttm'] if item_info['reg_dttm'] != '' else None
                    item_dict = {                        
                    "service_code": item_info['mdcode'],
                    "name": item_info["name"],
                    "type": item_info["type"],
                    "use_amt": item_info["pay_amt"],
                    "pay_amt": item_info["pay_amt"],
                    "region": None,
                    "start_date": start_date}
                    kt_item_charge_list.append(item_dict)

                if len(kt_item_charge_list) > 0:
                    kt_type_charge_df = pd.DataFrame(kt_item_charge_list)
                    group_list = ["service_code", "type"]
                    agg_dict = {"use_amt": "sum", "pay_amt": "sum"}
                    kt_type_charge_df = kt_type_charge_df.groupby(group_list, as_index=False).agg(agg_dict)
                    kt_type_charge_list = kt_type_charge_df.to_dict(orient="records")
                else:
                    kt_type_charge_list = []
                return kt_service_charge_list, kt_type_charge_list, kt_item_charge_list
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"서비스별 비용 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")