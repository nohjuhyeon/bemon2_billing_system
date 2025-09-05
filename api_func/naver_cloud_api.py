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

class NaverCloudApi():
    """
    네이버 클라우드 API를 호출하여 사용자, 서비스, 청구 데이터를 조회하고 처리하는 기능을 제공하는 클래스.

    Attributes:
        base_url (str): 네이버 클라우드 API의 기본 URL.
        access_key (str): API 호출을 위한 액세스 키.
        secret_key (str): API 호출을 위한 시크릿 키.

    주요 기능:
        1. API 호출(call_api): 특정 명령과 파라미터를 사용하여 API를 호출.
        2. 회원 목록 조회(member_list): 클라우드 사용자 목록을 가져옴.
        3. 서비스 목록 조회(service_list): 특정 사용자의 서비스 정보를 가져옴.
        4. 서비스 카테고리 조회(get_service_category): 서비스 카테고리 정보를 조회.
        5. 총 사용 요금 정보 조회(total_charge_info): 특정 사용자의 총 청구 정보를 조회.
        6. 서비스별 비용 정보 조회(service_charge_list): 서비스별, 타입별 및 아이템별 비용 정보를 조회.
    """

    def __init__(self,api_type):
        """
        NaverCloudApi 클래스의 초기화 메서드.

        Args:
            api_type (str): API 타입 ('공공' 또는 '민간').

        Variables:
            base_url (str): API의 기본 URL.
            access_key (str): API 호출을 위한 액세스 키.
            secret_key (str): API 호출을 위한 시크릿 키.

        주요 작업:
            1. API 타입에 따라 기본 URL과 액세스 키, 시크릿 키를 설정.
            2. 환경 변수에서 액세스 키와 시크릿 키를 가져옴.
        """
        if api_type == '공공':
            self.base_url = "https://billingapi.apigw.gov-ntruss.com"
            self.access_key = os.environ.get("NAVER_CLOUD_GOV_API_KEY")
            self.secret_key = os.environ.get("NAVER_CLOUD_GOV_SECRET_KEY")
        elif api_type == '민간':
            self.base_url = "https://billingapi.apigw.ntruss.com"
            self.access_key = os.environ.get("NAVER_CLOUD_PRIV_API_KEY")
            self.secret_key = os.environ.get("NAVER_CLOUD_PRIV_SECRET_KEY")
            

    # Signature 생성 함수
    def make_signature(self,signature_uri, current_timestamp, access_key, secret_key):
        """
        API 호출을 위한 Signature를 생성하는 메서드.

        Args:
            signature_uri (str): Signature를 생성할 URI.
            current_timestamp (str): 현재 타임스탬프.
            access_key (str): 액세스 키.
            secret_key (str): 시크릿 키.

        Returns:
            str: 생성된 Signature.

        Variables:
            method (str): HTTP 요청 메서드 (GET).
            message (str): Signature 생성에 필요한 메시지.
            signingKey (bytes): SHA256 해싱을 통해 생성된 Signature.

        주요 작업:
            1. 요청 메서드, URI, 타임스탬프, 액세스 키를 사용하여 메시지를 생성.
            2. 시크릿 키를 사용하여 SHA256 해싱 수행.
            3. Base64 인코딩된 Signature 반환.
        
        예외 처리:
            - KeyError: 필요한 키가 없을 경우 발생.
            - IndexError: 잘못된 값이 있을 경우 발생.
            - ValueError: 값 오류가 있을 경우 발생.
            - TypeError: 타입 오류가 있을 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력.
        """
        try:
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

        except KeyError as e:
            raise (f"Signature 생성에 필요한 키가 없습니다: {e}")
        except IndexError as e:
            raise (f"Signature 생성에 필요한 값이 잘못되었습니다: {e}")
        except ValueError as e:
            raise (f"Signature 생성 중 값 오류가 발생하였습니다: {e}")
        except TypeError as e:
            raise (f"Signature 생성 중 타입 오류가 발생하였습니다: {e}")
        except Exception as e:
            raise (f"Signature 생성 중 오류가 발생하였습니다: {e}")

    # API 호출 함수
    def call_api(self,command_uri, params_list):
        """
        네이버 클라우드 API를 호출하는 메서드.

        Args:
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출에 필요한 파라미터.

        Returns:
            dict: API 응답 데이터를 담은 딕셔너리. HTTP 요청이 실패하면 None 반환.

        Variables:
            current_timestamp (str): 현재 타임스탬프.
            query_params (dict): API 호출을 위한 쿼리 파라미터.
            headers (dict): API 호출을 위한 헤더.
            response (requests.Response): HTTP 응답 객체.

        주요 작업:
            1. API 호출 URL과 파라미터를 설정.
            2. Signature 생성 및 헤더 설정.
            3. GET 요청을 보내고 응답 데이터를 JSON 형식으로 변환.
            4. HTTP 요청 실패 시 오류 메시지를 출력.

        예외 처리:
            - requests.exceptions.RequestException: HTTP 요청 중 발생하는 오류를 처리.
            - json.JSONDecodeError: 응답 데이터 파싱 중 발생하는 오류를 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력.
        """
        try:
            # API URL 및 쿼리 파라미터
            current_timestamp = str(int(time.time() * 1000))

            query_params = {"responseFormatType": "json"}
            for i in params_list.keys():
                query_params[i] = params_list[i]

            # 쿼리 파라미터를 포함한 URL 생성
            full_url = f"{self.base_url}{command_uri}"
            response_url = requests.Request("GET", full_url, params=query_params).prepare().url
            signature_uri = response_url.replace(self.base_url, "")
            # 헤더 설정
            headers = {
                "x-ncp-apigw-timestamp": current_timestamp,
                "x-ncp-iam-access-key": self.access_key,
                "x-ncp-apigw-signature-v2": self.make_signature(
                    signature_uri, current_timestamp, self.access_key, self.secret_key
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
                raise ("API 호출 중 오류가 발생하였습니다.")
        except requests.exceptions.RequestException as e:
            raise (f"HTTP 요청 중 오류가 발생하였습니다: {e}")
        except json.JSONDecodeError as e:
            raise (f"응답 데이터 파싱 중 오류가 발생하였습니다: {e}")
        except Exception as e:
            raise (f"API 호출 중 알 수 없는 오류가 발생하였습니다: {e}")

    def member_list(self,startMonth, endMonth):
        """
        네이버 클라우드 사용자 목록을 조회하는 메서드.

        Args:
            startMonth (str): 조회 시작 월 (YYYYMM 형식).
            endMonth (str): 조회 종료 월 (YYYYMM 형식).

        Returns:
            list: 사용자 목록을 담은 딕셔너리 리스트.

        Variables:
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출 파라미터.
            data_dict (dict): API 응답 데이터.
            naver_member_list (list): 사용자 목록을 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 사용자 목록을 조회.
            2. 응답 데이터를 파싱하여 사용자 ID를 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command_uri = "/billing/v1/cost/getPartnerDemandCostList"
            params_list = {"startMonth": startMonth, "endMonth": endMonth}

            # API 호출 및 결과 처리
            data_dict =self.call_api(command_uri, params_list)
            naver_member_list = []
            for i in data_dict["getPartnerDemandCostListResponse"]["partnerDemandCostList"]:
                naver_member_list.append({"cloud_key": i["memberNo"]})
            return naver_member_list
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except IndexError as e: 
            raise(f"사용자 목록이 존재하지 않습니다: {e}")
        except Exception as e:
            raise(f"사용자 목록 조회 시 오류가 발생하였습니다: {e}")
        
    def service_list(self,memberNoList, contractMonth):
        """
        특정 사용자의 서비스 정보를 조회하는 메서드.

        Args:
            memberNoList (list): 사용자 번호 리스트.
            contractMonth (str): 계약 월 (YYYYMM 형식).

        Returns:
            list: 사용자 서비스 정보를 담은 딕셔너리 리스트.

        Variables:
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출 파라미터.
            data_dict (dict): API 응답 데이터.
            naver_service_list (list): 서비스 정보를 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 특정 사용자의 서비스 정보를 조회.
            2. 응답 데이터를 파싱하여 서비스 코드와 이름을 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command_uri = "/billing/v1/cost/getContractSummaryList"
            params_list = {
                "contractMonth": str(contractMonth),
                "isPartner": "true",
                "memberNoList": memberNoList,
            }

            # API 호출 및 결과 처리
            data_dict =self.call_api(command_uri, params_list)
            naver_service_list = []
            for i in data_dict["getContractSummaryListResponse"]["contractSummaryList"]:
                naver_service_list.append(
                    {
                        "code_name": i["contractType"]["codeName"],
                        "code": i["contractType"]["code"],
                    }
                )
            # 결과를 XML 파일로 저장
            return naver_service_list
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except IndexError as e: 
            raise(f"서비스 정보가 존재하지 않습니다: {e}")
        except Exception as e:
            raise(f"서비스 정보 조회 시 오류가 발생하였습니다: {e}")

    def get_service_category(self):
        """
        네이버 클라우드 서비스 카테고리 정보를 조회하는 메서드.

        Returns:
            dict: 서비스 카테고리 정보를 담은 딕셔너리. 각 카테고리는 'demandType' 코드를 키로 사용하며,
                해당 서비스의 타입, 이름, 코드 정보를 포함.

        Variables:
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출 파라미터.
            data_dict (dict): API 응답 데이터.
            dict_category (dict): 서비스 카테고리 정보를 저장하는 딕셔너리.

        주요 작업:
            1. API를 호출하여 서비스 카테고리 정보를 조회.
            2. 응답 데이터를 파싱하여 각 'demandType' 코드에 대한 서비스 정보를 정리.
            3. 'demandType' 코드가 중복되거나 데이터가 일치하지 않는 경우 처리.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command_uri = "/billing/v1/cost/getCostRelationCodeList"
            params_list = {}

            # API 호출 및 결과 처리
            data_dict =self.call_api(command_uri, params_list)
            dict_category = {}
            for i in data_dict["getCostRelationCodeListResponse"]["costRelationCodeList"]:
                if i["demandType"]["code"] not in dict_category.keys():
                    dict_category[i["demandType"]["code"]] = {
                            "type": i["productItemKind"]["codeName"],
                            "service_name": i["productCategory"]["codeName"],
                            "service_code": i["productCategory"]["code"],
                        }
                elif (dict_category[i["demandType"]["code"]]['type'] !=  i["productItemKind"]["code"] or 
                dict_category[i["demandType"]["code"]]['service_name'] !=  i["productCategory"]["code"]):
                    pass
            
            return dict_category
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except IndexError as e:
            raise(f"서비스 카테고리 정보가 존재하지 않습니다: {e}")
        except Exception as e:
            raise(f"서비스 카테고리 조회 시 오류가 발생하였습니다: {e}")

    def total_charge_info(self,memberNoList, bill_month):
        """
        특정 사용자의 총 청구 정보를 조회하는 메서드.

        Args:
            memberNoList (list): 사용자 번호 리스트.
            bill_month (str): 청구 월 (YYYYMM 형식).

        Returns:
            dict: 총 청구 정보를 담은 딕셔너리. 데이터가 없거나 여러 개일 경우 예외 발생.

        Variables:
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출 파라미터.
            data_dict (dict): API 응답 데이터.
            naver_total_charge_info (list): 총 청구 정보를 저장하는 리스트.
            discount_list (list): 각 사용자에 대한 할인 금액 리스트.
            total_discount_amt (float): 할인 금액의 총합.

        주요 작업:
            1. API를 호출하여 특정 사용자의 총 청구 정보를 조회.
            2. 응답 데이터를 파싱하여 필요한 정보를 정리.
            3. 할인 금액을 계산하여 총 청구 정보에 포함.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            command_uri = "/billing/v1/cost/getPartnerDemandCostList"
            params_list = {
                "startMonth": str(bill_month),
                "endMonth": str(bill_month),
                "memberNoList": memberNoList,
            }

            # API 호출 및 결과 처리
            data_dict =self.call_api(command_uri, params_list)
            naver_total_charge_info = []
            for i in data_dict["getPartnerDemandCostListResponse"]["partnerDemandCostList"]:

                discount_list = [
                    i["promiseDiscountAmount"],
                    i["promotionDiscountAmount"],
                    i["etcDiscountAmount"],
                    i["memberPromiseDiscountAddAmount"],
                    i["memberPriceDiscountAmount"],
                    i["customerDiscountAmount"],
                    i["productDiscountAmount"],
                    i["creditDiscountAmount"],
                    i["rounddownDiscountAmount"],
                    i["currencyDiscountAmount"]
                    ]
                total_discount_amt = sum(discount_list)
                
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
                        "pay_amt_including_vat": i["currencyPartnerTotalDemandAmountIncludingVat"]
                    }
                )
            if len(naver_total_charge_info) == 1:
                return naver_total_charge_info[0]
            else:
                raise("총 사용 요금 정보가 존재하지 않거나 여러 개입니다.")
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except IndexError as e: 
            raise(f"총 청구 정보가 존재하지 않습니다: {e}")
        except Exception as e:
            raise(f"총 청구 정보 조회 시 오류가 발생하였습니다: {e}")

    def service_charge_list(self,user_id,bill_month):
        """
        특정 사용자의 서비스별, 타입별, 아이템별 비용 정보를 조회하는 메서드.

        Args:
            user_id (str): 사용자 ID.
            bill_month (str): 청구 월 (YYYYMM 형식).

        Returns:
            tuple: 서비스별, 타입별, 아이템별 비용 정보를 담은 리스트.

        Variables:
            product_item_kind (dict): 서비스 카테고리 정보를 담은 딕셔너리.
            command_uri (str): API 명령어 URI.
            params_list (dict): API 호출 파라미터.
            data_dict (dict): API 응답 데이터.
            response_data (list): 서비스별 비용 정보를 저장하는 리스트.
            naver_item_charge_list (list): 아이템별 비용 정보를 저장하는 리스트.
            naver_type_charge_list (list): 타입별 비용 정보를 저장하는 리스트.
            naver_service_charge_list (list): 서비스별 비용 정보를 저장하는 리스트.

        주요 작업:
            1. API를 호출하여 서비스별 비용 정보를 조회.
            2. 응답 데이터를 파싱하여 서비스별, 타입별, 아이템별 비용 정보를 정리.
            3. 데이터프레임을 사용하여 비용 정보를 그룹화 및 집계.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - ValueError: 데이터 처리 중 오류가 발생할 경우 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            product_item_kind = self.get_service_category()

            command_uri = "/billing/v1/cost/getContractDemandCostList"
            params_list = {
                "startMonth": str(bill_month),
                "endMonth": str(bill_month),
                "isPartner": "true",
                "memberNoList": [user_id],
            }
            # API 호출 및 결과 처리
            data_dict =self.call_api(command_uri, params_list)
            response_data = []
            for i in data_dict["getContractDemandCostListResponse"]["contractDemandCostList"]:
                total_discount_amt = i["promotionDiscountAmount"] + i["etcDiscountAmount"] + i["promiseDiscountAmount"]

                if "instanceName" in i["contract"].keys():
                    name = i["contract"]["instanceName"]
                    start_date = i['contract']['contractStartDate']
                    end_date = i["contract"]["contractEndDate"]
                else:
                    name = i["demandTypeDetail"]["codeName"]
                    start_date = ''
                    end_date = ''

                type_name = product_item_kind[i["demandType"]["code"]]["type"]
                service_name = product_item_kind[i["demandType"]["code"]]["service_name"]
                service_code = product_item_kind[i["demandType"]["code"]]["service_code"]
                
                response_data.append(
                    {
                        "cloud_key": user_id,
                        "service_code": service_code,
                        "service": service_name,
                        "bill_month": int(i["demandMonth"]),
                        "type": type_name,
                        "name": name,
                        "region": i["regionCode"],
                        "use_amt": i["useAmount"],
                        "total_discount_amt": total_discount_amt,
                        "pay_amt": i["demandAmount"],
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
            response_df = pd.DataFrame(response_data)

            # item 별 use_amt, pay_amt, total_discount_amt 합계 계산
            group_list = ["cloud_key","service_code","service","bill_month","type","name","region","start_date","end_date"]
            agg_dict = {"use_amt": "sum", "total_discount_amt": "sum", "pay_amt": "sum"}
            naver_item_charge_df = response_df.groupby(group_list,as_index=False).agg(agg_dict)

            # naver_item_charge_df에 한 번에 적용
            naver_item_charge_df["start_date"] = naver_item_charge_df["start_date"].apply(
                lambda x: None if x == "" else datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
            )
            naver_item_charge_list = naver_item_charge_df.to_dict(orient="records")


            # type 별 use_amt, pay_amt 합계 계산
            naver_type_charge_df = pd.DataFrame(naver_item_charge_list)
            group_list = ["cloud_key","service_code","service","bill_month","type"]
            agg_dict = {"use_amt": "sum", "pay_amt": "sum"}
            naver_type_charge_df = naver_type_charge_df.groupby(group_list,as_index=False).agg(agg_dict)
            naver_type_charge_list = naver_type_charge_df.to_dict(orient="records")

            # service 별 use_amt, pay_amt, total_discount_amt 합계 계산
            naver_service_charge_df = pd.DataFrame(naver_item_charge_list)
            group_list = ["cloud_key","service_code","service","bill_month"]
            agg_dict = {"use_amt": "sum", "pay_amt": "sum","total_discount_amt":"sum"}
            naver_service_charge_df = naver_service_charge_df.groupby(group_list,as_index=False).agg(agg_dict)
            naver_service_charge_list = naver_service_charge_df.to_dict(orient="records")

            return naver_service_charge_list, naver_type_charge_list, naver_item_charge_list
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except IndexError as e: 
            raise(f"서비스별 비용 정보가 존재하지 않습니다: {e}")
        except ValueError as e:
            raise(f"데이터 처리 중 오류가 발생하였습니다: {e}")
        except Exception as e:
            raise(f"서비스별 비용 정보 조회 시 오류가 발생하였습니다: {e}")
