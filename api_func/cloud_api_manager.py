from datetime import datetime
from db_func.data_controller import DataController
from api_func.naver_cloud_api import NaverCloudApi
from api_func.kt_cloud_api import KtCloudApi
from api_func.nhn_cloud_api import NhnCloudApi


class CloudApiManager:
    """
    클라우드 청구 데이터를 API를 통해 조회하고 데이터베이스를 업데이트하는 기능을 제공하는 클래스.

    Attributes:
        db (DataController): 데이터베이스 연결 객체로, 데이터 조회 및 삽입을 관리.
        end_date (int): 데이터 업데이트 종료 날짜 (YYYYMM 형식).

    주요 기능:
        1. 클라우드 서비스에 따라 적절한 API를 선택(api_select).
        2. 총 사용 요금 정보를 조회(total_charge_info_api).
        3. 서비스별 사용 요금 정보를 조회(service_charge_info_api).
        4. 타입별 사용 요금 정보를 조회(type_charge_info_api).
        5. 아이템별 사용 요금 정보를 조회(item_charge_info_api).
    """

    def __init__(self):
        """
        CloudApiManager 클래스의 초기화 메서드.

        주요 작업:
            1. 데이터베이스 연결 객체(DataController)를 초기화.
            2. 종료 날짜를 현재 날짜 기준으로 YYYYMM 형식으로 설정.
        """
        self.db = DataController()
        self.end_date = int(datetime.today().strftime("%Y%m"))

    def api_select(self, cloud_info):
        """
        클라우드 정보를 기반으로 적절한 API를 선택하는 메서드.

        Args:
            cloud_info (dict): 클라우드 정보가 담긴 딕셔너리. 
                               CLOUD_NAME(클라우드 이름)과 CLOUD_CLASS(클라우드 클래스)를 포함.

        Returns:
            tuple: 선택된 클라우드 API 객체와 관련 키 이름.

        Variables:
            cloud_api (object): 선택된 클라우드 API 객체.
            cloud_key (str): 클라우드 사용자 식별 키.

        주요 작업:
            1. 클라우드 이름에 따라 적절한 API 객체를 반환.
            2. 사용자 식별 키를 함께 반환.
        """
        if cloud_info["CLOUD_NAME"] == "NAVER":
            return NaverCloudApi(cloud_info['CLOUD_CLASS']), 'CLOUD_USER_NUM'
        if cloud_info["CLOUD_NAME"] == "KT":
            return KtCloudApi(cloud_info['CLOUD_CLASS']), 'CLOUD_USER_ID'
        if cloud_info["CLOUD_NAME"] == "NHN":
            return NhnCloudApi(cloud_info['CLOUD_CLASS']), None

    def total_charge_info_api(self, cloud_element, bill_month):
        """
        총 사용 요금 정보를 API를 통해 조회하는 메서드.

        Args:
            cloud_element (dict): 클라우드 요소 정보.
            bill_month (int): 청구 월 (YYYYMM 형식).

        Returns:
            total_charge_dict (dict): 총 사용 요금 정보를 담은 딕셔너리.
            total_cloud_charge_dict (dict): 클라우드별 요금 정보를 담은 딕셔너리.

        Variables:
            total_charge_info (dict): API 응답에서 가져온 총 사용 요금 정보.
            total_charge_dict (dict): 총 사용 요금 정보를 정리한 딕셔너리.
            total_cloud_charge_dict (dict): 클라우드별 요금 정보를 정리한 딕셔너리.
            cloud_api (object): 선택된 클라우드 API 객체.
            cloud_key (str): 클라우드 사용자 식별 키.

        주요 작업:
            1. 클라우드 API를 통해 총 사용 요금 정보를 조회.
            2. 조회된 데이터를 정리하여 반환.

        예외 처리:
            - KeyError: 클라우드 정보 딕셔너리에 필요한 키가 없을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - TypeError: 응답 데이터 타입이 예상과 다를 경우 발생.
            - ValueError: 응답 데이터 값이 예상과 다를 경우 발생.
            - AttributeError: 클라우드 API 객체에 필요한 메서드가 없을 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            cloud_api, cloud_key = self.api_select(cloud_element)
            total_charge_info = cloud_api.total_charge_info(cloud_element[cloud_key], bill_month)
            total_charge_dict = None
            total_cloud_charge_dict = None
            if total_charge_info:
                total_charge_dict = {
                    "CLOUD_ID": cloud_element["CLOUD_ID"],
                    "BILL_MONTH": bill_month,
                    "TOTAL_COIN_USE_AMT": total_charge_info["coin_use_amt"],
                    "TOTAL_DEFAULT_AMT": total_charge_info["default_amt"],
                    "TOTAL_USE_AMT": total_charge_info["use_amt"],
                    "TOTAL_DISCOUNT_AMT": total_charge_info["total_discount_amt"],
                    "TOTAL_VAT_AMT": total_charge_info["vat_amt"],
                    "TOTAL_VAT_INCLUDE_AMT": total_charge_info["pay_amt_including_vat"],
                    "TOTAL_PAY_AMT": total_charge_info["pay_amt"],
                    "TOTAL_USER_PAY_AMT": total_charge_info["pay_amt"],
                    "TOTAL_DISCOUNT_INCLUDE_AMT": total_charge_info["pay_amt"],
                }
                total_cloud_charge_dict = {
                    "TOTAL_CLOUD_USE_AMT": total_charge_info["use_amt"],
                    "TOTAL_CLOUD_DISCOUNT_AMT": total_charge_info["total_discount_amt"],
                    "TOTAL_CLOUD_VAT_AMT": total_charge_info["vat_amt"],
                    "TOTAL_CLOUD_VAT_INCLUDE_AMT": total_charge_info["pay_amt_including_vat"],
                    "TOTAL_CLOUD_PAY_AMT": total_charge_info["pay_amt"],
                    "TOTAL_CLOUD_USER_PAY_AMT": total_charge_info["pay_amt"],
                }
            return total_charge_dict, total_cloud_charge_dict
        except KeyError as e:
            raise (f"클라우드 정보에 필요한 키가 없습니다: {e}") 
        except IndexError as e:
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except TypeError as e:
            raise (f"응답 데이터 타입이 예상과 다릅니다: {e}")
        except ValueError as e:
            raise (f"응답 데이터 값이 예상과 다릅니다: {e}")
        except AttributeError as e:
            raise (f"클라우드 API 객체에 필요한 메서드가 없습니다: {e}")
        except Exception as e:
            raise (f"총 사용 요금 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")

    def service_charge_info_api(self, total_charge_cloud_id, service_charge_api):
        """
        서비스별 사용 요금 정보를 API를 통해 조회하는 메서드.

        Args:
            total_charge_cloud_id (int): 총 사용 요금 ID.
            service_charge_api (list): 서비스 사용 요금 API 응답 데이터.

        Returns:
            service_charge_list (list): 서비스별 사용 요금 정보를 담은 리스트.

        Variables:
            service_charge_list (list): 서비스별 사용 요금 정보를 저장하는 리스트.
            service_charge_dict (dict): 개별 서비스 사용 요금 정보를 저장하는 딕셔너리.

        주요 작업:
            1. 서비스별 사용 요금 데이터를 정리하여 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            service_charge_list = []
            for service_charge_element in service_charge_api:
                service_charge_dict = {
                    "TOTAL_CHARGE_CLOUD_ID": total_charge_cloud_id,
                    "CLOUD_SERVICE_CHARGE_NAME": service_charge_element["service"],
                    "CLOUD_SERVICE_CHARGE_CODE": service_charge_element["service_code"],
                    "CLOUD_SERVICE_USE_AMT": service_charge_element["use_amt"],
                    "CLOUD_SERVICE_DISCOUNT_AMT": service_charge_element["total_discount_amt"],
                    "CLOUD_SERVICE_PAY_AMT": service_charge_element["pay_amt"],
                }
                service_charge_list.append(service_charge_dict)

            return service_charge_list
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"서비스별 사용 요금 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")

    def type_charge_info_api(self, total_charge_cloud_id, type_charge_api):
        """
        타입별 사용 요금 정보를 API를 통해 조회하는 메서드.

        Args:
            total_charge_cloud_id (int): 총 사용 요금 ID.
            type_charge_api (list): 타입별 사용 요금 API 응답 데이터.

        Returns:
            type_charge_list (list): 타입별 사용 요금 정보를 담은 리스트.
            service_id_dict (dict): 서비스별 ID 매핑 정보를 담은 딕셔너리.

        Variables:
            type_charge_list (list): 타입별 사용 요금 정보를 저장하는 리스트.
            service_id_dict (dict): 서비스별 ID 매핑 정보를 저장하는 딕셔너리.
            type_id_dict (dict): 타입별 ID 매핑 정보를 저장하는 딕셔너리.
            service_code (str): 서비스 코드.
            selected_service_charge_info (dict): 선택된 서비스별 사용 요금 정보.
            selected_service_charge_id (int): 선택된 서비스별 사용 요금 ID.
            type_name (str): 타입 이름.
            selected_type_charge_info (dict): 선택된 타입별 사용 요금 정보.
            selected_type_charge_ID (int): 선택된 타입별 사용 요금 ID.

        주요 작업:
            1. 타입별 사용 요금 데이터를 정리하여 리스트로 반환.
            2. 서비스별 ID 매핑 정보를 생성.
            3. 서비스 코드와 타입 이름을 키로 사용하여 매핑 딕셔너리를 생성.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.        
        """
        try:
            type_charge_list = []
            service_id_dict = {}
            for type_charge_element in type_charge_api:
                type_id_dict = {}
                service_code = type_charge_element["service_code"]
                service_charge_select_condition = {
                    "TOTAL_CHARGE_CLOUD_ID": total_charge_cloud_id,
                    "CLOUD_SERVICE_CHARGE_CODE": service_code,
                }
                selected_service_charge_info = self.db.select_one("CHARGE_CLOUD_SERVICE_LIST", "CLOUD_SERVICE_CHARGE_ID", service_charge_select_condition)
                selected_service_charge_id = selected_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
                type_charge_dict = {
                    "CLOUD_SERVICE_CHARGE_ID": selected_service_charge_id,
                    "TYPE_NAME": type_charge_element["type"],
                    "TYPE_USE_AMT": type_charge_element["use_amt"],
                    "TYPE_PAY_AMT": type_charge_element["pay_amt"],
                    "TYPE_USER_PAY_AMT": type_charge_element["pay_amt"],
                }
                type_charge_list.append(type_charge_dict)
                type_name = type_charge_element["type"]
                if service_code not in service_id_dict.keys():
                    type_id_dict[type_name] = selected_service_charge_id
                    service_id_dict[service_code] = type_id_dict
                else:
                    service_id_dict[service_code][type_name] = selected_service_charge_id

            return type_charge_list, service_id_dict
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"타입별 사용 요금 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")

    def item_charge_info_api(self, service_id_dict, item_charge_api):
        """
        아이템별 사용 요금 정보를 API를 통해 조회하는 메서드.

        Args:
            service_id_dict (dict): 서비스별 ID 매핑 정보.
            item_charge_api (list): 아이템별 사용 요금 API 응답 데이터.

        Returns:
            item_charge_list (list): 아이템별 사용 요금 정보를 담은 리스트.

        Variables:
            item_charge_list (list): 아이템별 사용 요금 정보를 저장하는 리스트.
            item_id_dict (dict): 아이템별 ID 매핑 정보를 저장하는 딕셔너리.
            type_name (str): 타입 이름.
            service_code (str): 서비스 코드.
            service_charge_id (int): 서비스별 사용 요금 ID.
            selected_type_charge_info (dict): 선택된 타입별 사용 요금 정보.
            selected_type_charge_ID (int): 선택된 타입별 사용 요금 ID.

        주요 작업:
            1. 아이템별 사용 요금 데이터를 정리하여 리스트로 반환.
        
        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - IndexError: 응답 데이터가 비어 있거나 예상과 다른 형식일 경우 발생.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            item_charge_list = []
            for item_charge_element in item_charge_api:
                service_code = item_charge_element['service_code']
                type_name = item_charge_element['type']
                service_charge_id = service_id_dict[service_code][type_name]
                
                type_charge_select_condition = {
                    "CLOUD_SERVICE_CHARGE_ID": service_charge_id,
                    "TYPE_NAME": item_charge_element["type"],
                }
                selected_type_charge_info = self.db.select_one("TYPE_CHARGE_LIST", "TYPE_CHARGE_ID", type_charge_select_condition)
                selected_type_charge_ID = selected_type_charge_info["TYPE_CHARGE_ID"]
                item_charge_dict = {
                    "TYPE_CHARGE_ID": selected_type_charge_ID,
                    "ITEM_NAME": item_charge_element["name"],
                    "ITEM_REGION": item_charge_element["region"],
                    "ITEM_USE_AMT": item_charge_element["use_amt"],
                    "ITEM_PAY_AMT": item_charge_element["pay_amt"],
                    "ITEM_USER_PAY_AMT": item_charge_element["pay_amt"],
                    "ITEM_START_DATE": item_charge_element["start_date"],
                }
                item_charge_list.append(item_charge_dict)
            return item_charge_list
        except KeyError as e:
            raise (f"응답 데이터에서 누락된 키가 있습니다: {e}")
        except IndexError as e: 
            raise (f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except Exception as e:
            raise (f"아이템별 사용 요금 정보 조회 중 알 수 없는 오류가 발생하였습니다: {e}")
