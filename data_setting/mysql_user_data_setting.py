from data_setting.MYSQL_CRUD import MySQLDatabase
from datetime import datetime, timedelta
import logging
from dateutil.relativedelta import relativedelta
import json
import mysql.connector
import os 
from api_func.gov import gov_kt_cloud_api, gov_naver_cloud_api, gov_nhn_cloud_api
from api_func.private import (
    private_kt_cloud_api,
    private_naver_cloud_api,
    private_nhn_cloud_api,
)
import os

class BillingDatabaseUpdater:
    """
    청구 시스템 데이터베이스 업데이트를 관리하는 클래스입니다.

    Attributes:
        db (MySQLDatabase): 데이터베이스 연결 객체.
        end_date (int): 데이터 업데이트 종료 날짜 (YYYYMM 형식).
        file_path (str): SQL 파일의 경로.
        host (str): MySQL 서버 호스트.
        port (int): MySQL 서버 포트.
        user (str): MySQL 사용자 이름.
        password (str): MySQL 사용자 비밀번호.
        database (str): 생성할 데이터베이스 이름.
    """

    def __init__(self):
        """
        BillingDatabaseUpdater 클래스의 초기화 메서드입니다.
        
        데이터베이스 연결을 설정하고, 환경 변수에서 MySQL 연결 정보를 가져옵니다.
        종료 날짜를 초기화하며, SQL 파일 경로를 설정합니다.
        """
        self.db = MySQLDatabase()
        self.end_date = int(datetime.today().strftime("%Y%m"))
        self.file_path='data_setting/bemon2.sql'
        self.host=os.environ.get("MYSQL_HOST")
        self.port=os.environ.get("MYSQL_PORT")
        self.user=os.environ.get("MYSQL_USER")
        self.password=os.environ.get("MYSQL_PASSWORD")
        self.database=os.environ.get("MYSQL_DATABASE")
        print(f"Connecting to MySQL with host={self.host}, user={self.user}, port={self.port}")


    def api_select(self, cloud_info):
        """
        클라우드 정보를 기반으로 적절한 API를 선택합니다.

        Args:
            cloud_info (dict): 클라우드 정보가 담긴 딕셔너리. CLOUD_NAME과 CLOUD_CLASS를 포함합니다.

        Returns:
            function: 선택된 클라우드 API 함수.
        """
        if cloud_info["CLOUD_NAME"] == "NAVER":
            return gov_naver_cloud_api if cloud_info["CLOUD_CLASS"] == "공공" else private_naver_cloud_api,'CLOUD_USER_NUM'
        if cloud_info["CLOUD_NAME"] == "KT":
            return gov_kt_cloud_api if cloud_info["CLOUD_CLASS"] == "공공" else private_kt_cloud_api,'CLOUD_USER_ID'
        if cloud_info["CLOUD_NAME"] == "NHN":
            return gov_nhn_cloud_api,None if cloud_info["CLOUD_CLASS"] == "공공" else private_nhn_cloud_api,None

    def load_json(self, file_path: str) -> list:
        """
        지정된 경로에서 JSON 파일을 로드합니다.

        Args:
            file_path (str): JSON 파일의 경로.

        Returns:
            list: JSON 파일에서 로드된 데이터 리스트. 파일이 없으면 빈 리스트를 반환합니다.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def create_database_from_sql(self):
        """
        SQL 파일을 기반으로 MySQL 데이터베이스를 생성합니다.

        Args:
            file_path (str): SQL 파일의 경로.
            host (str): MySQL 서버 호스트.
            port (int): MySQL 서버 포트.
            user (str): MySQL 사용자 이름.
            password (str): MySQL 사용자 비밀번호.
            database (str): 생성할 데이터베이스 이름.
        """
        # MySQL 데이터베이스에 연결
        connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password
        )

        cursor = connection.cursor()

        # 데이터베이스 생성
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
        cursor.execute(f"USE {self.database}")

        # SQL 파일 읽기
        with open(self.file_path, 'r', encoding='utf-8-sig') as file:
            sql_commands = file.read()

        # SQL 명령어 실행
        for command in sql_commands.split(';'):
            if command.strip():
                try:
                    cursor.execute(command)
                except mysql.connector.Error as err:
                    print(f"Error: {err}")
                    print(f"Command: {command}")

        # 연결 종료
        cursor.close()
        connection.close()


    def generate_month_range(self, start_date, end_date):
        """
        시작 날짜와 종료 날짜 사이의 월 범위를 생성합니다.

        Args:
            start_date (int): 시작 날짜 (YYYYMM 형식).
            end_date (int): 종료 날짜 (YYYYMM 형식).

        Returns:
            list: 시작 날짜와 종료 날짜 사이의 월 리스트.
        """
        start = datetime.strptime(str(start_date), "%Y%m")
        end = datetime.strptime(str(end_date), "%Y%m")
        month_list = []
        while start <= end:
            month_list.append(int(start.strftime("%Y%m")))
            start += timedelta(days=31)
            start = start.replace(day=1)
        return month_list

    def user_list_insert(self):
        """
        사용자 정보를 데이터베이스에 삽입합니다.

        사용자 정보는 JSON 파일에서 로드되며, 사용자와 클라우드 정보를 각각 USER_LIST와 CLOUD_LIST 테이블에 삽입합니다.
        """
        user_list = self.load_json("data_setting/member_info.json")
        for user_dict in user_list:
            user_data_dict = {"USER_NAME": user_dict["user_name"]}
            self.db.insert("USER_LIST", user_data_dict)

            selected_user_dict = self.db.select_one("USER_LIST", None, user_data_dict)
            for cloud_dict in user_dict["cloud_list"]:
                cloud_dict["user_id"] = selected_user_dict["USER_ID"]
                cloud_dict["user_name"] = selected_user_dict["USER_NAME"]
                cloud_data_dict = {
                    "USER_ID": cloud_dict["user_id"],
                    "CLOUD_NAME": cloud_dict["cloud_name"],
                    "CLOUD_CLASS": cloud_dict["cloud_class"],
                    "CLOUD_USER_ID": cloud_dict["cloud_user_id"],
                    "CLOUD_USER_NUM": cloud_dict["cloud_user_num"],
                    "START_DATE": cloud_dict["start_date"],
                }
                self.db.insert("CLOUD_LIST", cloud_data_dict)

    def service_list_update(self):
        """
        서비스 목록을 데이터베이스에 업데이트합니다.

        각 클라우드 요소에 대해 API를 호출하여 서비스 목록을 가져오고, 새로운 서비스 코드를 SERVICE_LIST 테이블에 삽입합니다.
        """
        current_cloud_list = self.db.select_many("CLOUD_LIST", None)
        for cloud_element in current_cloud_list:
            cloud_api,cloud_key = self.api_select(cloud_element)
            cloud_select_condition = {"CLOUD_ID": cloud_element["CLOUD_ID"]}
            current_service_list = self.db.select_many("SERVICE_LIST", "SERVICE_CODE", cloud_select_condition)
            current_service_code_list = [i["SERVICE_CODE"] for i in current_service_list]
            service_list = cloud_api.service_list(cloud_element[cloud_key], self.end_date) if cloud_element["CLOUD_NAME"] == "NAVER" else cloud_api.service_list(cloud_element[cloud_key])
            for service_element in service_list:
                if service_element["code"] not in current_service_code_list:
                    service_insert_dict = {
                        "CLOUD_ID": cloud_element["CLOUD_ID"],
                        "SERVICE_NAME": service_element["code_name"],
                        "SERVICE_CODE": service_element["code"],
                    }
                    self.db.insert("SERVICE_LIST", service_insert_dict)

    def total_charge_info_api(self, cloud_element, bill_month):
        """
        총 사용 요금 정보를 API를 통해 가져옵니다.

        Args:
            cloud_element (dict): 클라우드 요소 정보.
            bill_month (int): 청구 월 (YYYYMM 형식).

        Returns:
            dict: 총 사용 요금 정보를 담은 딕셔너리.
        """
        cloud_api,cloud_key = self.api_select(cloud_element)
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
            total_cloud_charge_dict =  {
                "TOTAL_CLOUD_USE_AMT": total_charge_info["use_amt"],
                "TOTAL_CLOUD_DISCOUNT_AMT": total_charge_info["total_discount_amt"],
                "TOTAL_CLOUD_VAT_AMT": total_charge_info["vat_amt"],
                "TOTAL_CLOUD_VAT_INCLUDE_AMT": total_charge_info["pay_amt_including_vat"],
                "TOTAL_CLOUD_PAY_AMT": total_charge_info["pay_amt"],
                "TOTAL_CLOUD_USER_PAY_AMT": total_charge_info["pay_amt"],
            }
        return total_charge_dict,total_cloud_charge_dict

    def service_to_charge_update(self,service_name,cloud_id,total_charge_id,service_total_notes=None):
        service_select_condtion = {"CLOUD_ID": cloud_id}
        service_table_name = service_name + "_LIST"
        service_use_amt_key = service_name + "_USE_AMT"
        service_user_pay_amt_key = service_name + "_USER_PAY_AMT"
        charge_service_table_name = "CHARGE_" + service_table_name
        charge_service_id = "CHARGE_"+service_name + "_ID"
        total_charge_service_table_name = "TOTAL_"+charge_service_table_name
        total_service_use_amt_key = "TOTAL_CHARGE_"+service_use_amt_key
        total_service_user_pay_amt_key = "TOTAL_CHARGE_"+service_user_pay_amt_key
        total_service_id = "TOTAL_"+charge_service_id
        total_service_notes_key = "TOTAL_CHARGE_"+service_name + "_NOTES"
        service_list = self.db.select_many(service_table_name, None, service_select_condtion)
        service_total_use_amt = sum([service_element[service_use_amt_key]for service_element in service_list])
        service_total_user_pay_amt = sum([service_element[service_user_pay_amt_key]for service_element in service_list])
        service_total_dict = {
            "TOTAL_CHARGE_ID":total_charge_id,
            total_service_use_amt_key:service_total_use_amt,
            total_service_user_pay_amt_key:service_total_user_pay_amt,
            total_service_notes_key:service_total_notes
        }
        self.db.insert(total_charge_service_table_name,service_total_dict)
        total_charge_service_select_condition = {"TOTAL_CHARGE_ID":total_charge_id}
        total_charge_service_info = self.db.select_one(total_charge_service_table_name, total_service_id,total_charge_service_select_condition )
        total_charge_service_id = total_charge_service_info[total_service_id]
        for service_element in service_list:
            charge_service_dict = {total_service_id:total_charge_service_id}
            for service_element_key,service_element_value in service_element.items():
                if "ID" not in service_element_key:
                    charge_service_element_key = "CHARGE_"+service_element_key
                    charge_service_dict[charge_service_element_key] = service_element_value
            self.db.insert(charge_service_table_name,charge_service_dict)
        return service_total_use_amt,service_total_user_pay_amt
    def total_charge_list_update(self):
        """
        총 사용 요금 목록을 데이터베이스에 업데이트합니다.

        각 클라우드 요소에 대해 청구 월별로 요금 정보를 가져오고, TOTAL_CLOUD_CHARGE_LIST 테이블에 삽입 또는 업데이트합니다.
        """
        current_cloud_list = self.db.select_many("CLOUD_LIST", None)
        for cloud_element in current_cloud_list:
            period_list = self.generate_month_range(cloud_element["START_DATE"], self.end_date)
            for bill_month in period_list:
                total_charge_select_condition = {"CLOUD_ID": cloud_element["CLOUD_ID"], "BILL_MONTH": bill_month}
                current_total_charge_info = self.db.select_one("TOTAL_CHARGE_LIST", None, total_charge_select_condition)
                if not current_total_charge_info:
                    total_charge_dict,total_cloud_charge_dict = self.total_charge_info_api(cloud_element, bill_month)
                    if total_charge_dict and total_cloud_charge_dict:
                        self.db.insert("TOTAL_CHARGE_LIST", total_charge_dict)
                        current_total_charge_info = self.db.select_one("TOTAL_CHARGE_LIST", None, total_charge_select_condition)
                        total_charge_id = current_total_charge_info['TOTAL_CHARGE_ID']
                        total_cloud_charge_dict['TOTAL_CHARGE_ID'] = total_charge_id
                        total_cloud_charge_dict["TOTAL_CLOUD_NOTES"] = "마켓플레이스 3rd Party S/W 포함"
                        self.db.insert("TOTAL_CLOUD_CHARGE_LIST",total_cloud_charge_dict)
                        
                        third_party_use_amt,third_party_user_pay_amt = self.service_to_charge_update("THIRD_PARTY",cloud_element["CLOUD_ID"],total_charge_id,"마켓플레이스 외 3rd Party S/W")
                        total_charge_dict['TOTAL_USE_AMT'] += third_party_use_amt
                        total_charge_dict['TOTAL_USER_PAY_AMT'] += third_party_user_pay_amt
                        
                        managed_service_use_amt,managed_service_user_pay_amt = self.service_to_charge_update("MANAGED_SERVICE",cloud_element["CLOUD_ID"],total_charge_id,"")
                        total_charge_dict['TOTAL_USE_AMT'] += managed_service_use_amt
                        total_charge_dict['TOTAL_USER_PAY_AMT'] += managed_service_user_pay_amt
                        
                        other_managed_service_use_amt,other_service_user_pay_amt = self.service_to_charge_update("OTHER_SERVICE",cloud_element["CLOUD_ID"],total_charge_id,"")
                        total_charge_dict['TOTAL_USE_AMT'] += other_managed_service_use_amt
                        total_charge_dict['TOTAL_USER_PAY_AMT'] += other_service_user_pay_amt
                        self.db.update("TOTAL_CHARGE_LIST", total_charge_dict, total_charge_update_condition)
                        
                elif bill_month == self.end_date:
                    total_charge_dict,total_cloud_charge_dict = self.total_charge_info_api(cloud_element, bill_month)
                    if total_charge_dict and total_cloud_charge_dict:
                        total_charge_update_condition = {"TOTAL_CHARGE_ID": current_total_charge_info["TOTAL_CHARGE_ID"]}                
                        self.db.update("TOTAL_CHARGE_LIST", total_charge_dict, total_charge_update_condition)
                        current_total_charge_info = self.db.select_one("TOTAL_CHARGE_LIST", None, total_charge_select_condition)
                        total_charge_id = current_total_charge_info['TOTAL_CHARGE_ID']
                        total_cloud_charge_update_condition = {"TOTAL_CHARGE_CLOUD_ID": total_charge_id}                
                        total_cloud_charge_dict['TOTAL_CHARGE_ID'] = total_charge_id
                        self.db.update("TOTAL_CLOUD_CHARGE_LIST", total_cloud_charge_dict, total_cloud_charge_update_condition)

    def service_charge_info_api(self, cloud_element, total_cloud_charge_info,bill_month):
        """
        서비스 사용 요금 정보를 API를 통해 가져옵니다.

        Args:
            cloud_element (dict): 클라우드 요소 정보.
            total_charge_info (dict): 총 사용 요금 정보.

        Returns:
            tuple: 서비스 사용 요금 정보 리스트와 API 응답 데이터를 포함하는 튜플.
        """
        cloud_api,cloud_key = self.api_select(cloud_element)
        service_charge_api = cloud_api.service_charge_list(cloud_element[cloud_key], bill_month)

        service_charge_list = []
        for service_charge_element in service_charge_api:
            service_charge_dict = {
                "TOTAL_CHARGE_CLOUD_ID": total_cloud_charge_info["TOTAL_CHARGE_CLOUD_ID"],
                "CLOUD_SERVICE_CHARGE_NAME": service_charge_element["service"],
                "CLOUD_SERVICE_CHARGE_CODE": service_charge_element["service_code"],
                "CLOUD_SERVICE_USE_AMT": service_charge_element["use_amt"],
                "CLOUD_SERVICE_DISCOUNT_AMT": service_charge_element["total_discount_amt"],
                "CLOUD_SERVICE_PAY_AMT": service_charge_element["pay_amt"],
            }
            service_charge_element["TOTAL_CHARGE_CLOUD_ID"] = total_cloud_charge_info["TOTAL_CHARGE_CLOUD_ID"]
            service_charge_element["CLOUD_SERVICE_CHARGE_CODE"] = service_charge_element["service_code"]
            service_charge_list.append(service_charge_dict)
        return service_charge_list, service_charge_api

    def type_charge_info_api(self, service_charge_api):
        """
        아이템 사용 요금 정보를 API를 통해 가져옵니다.

        Args:
            service_charge_api (list): 서비스 사용 요금 API 응답 데이터.

        Returns:
            list: 아이템 사용 요금 정보를 담은 리스트.
        """
        type_charge_list = []
        for service_charge_element in service_charge_api:
            service_charge_select_condition = {
                "TOTAL_CHARGE_CLOUD_ID": service_charge_element["TOTAL_CHARGE_CLOUD_ID"],
                "CLOUD_SERVICE_CHARGE_CODE": service_charge_element["CLOUD_SERVICE_CHARGE_CODE"],
            }
            selected_service_charge_info = self.db.select_one("CHARGE_CLOUD_SERVICE_LIST", "CLOUD_SERVICE_CHARGE_ID", service_charge_select_condition)
            selected_service_charge_ID = selected_service_charge_info["CLOUD_SERVICE_CHARGE_ID"]
            new_service_list = []
            for item_element in service_charge_element["service_list"]:
                type_charge_dict = {
                    "CLOUD_SERVICE_CHARGE_ID": selected_service_charge_ID,
                    "TYPE_NAME": item_element["type"],
                    "TYPE_USE_AMT": item_element["type_use_amt"],
                    "TYPE_PAY_AMT": item_element["type_pay_amt"],
                    "TYPE_USER_PAY_AMT": item_element["type_pay_amt"],
                }
                type_charge_list.append(type_charge_dict)
                item_element["CLOUD_SERVICE_CHARGE_ID"] = selected_service_charge_ID
                new_service_list.append(item_element)
            service_charge_element['service_list'] = new_service_list
        return type_charge_list,service_charge_api

    def item_charge_info_api(self, service_charge_api):
        """
        아이템 사용 요금 정보를 API를 통해 가져옵니다.

        Args:
            service_charge_api (list): 서비스 사용 요금 API 응답 데이터.

        Returns:
            list: 아이템 사용 요금 정보를 담은 리스트.
        """
        item_charge_list = []
        for service_charge_element in service_charge_api:
            for type_list in service_charge_element["service_list"]:
                type_charge_select_condition = {
                    "CLOUD_SERVICE_CHARGE_ID": type_list["CLOUD_SERVICE_CHARGE_ID"],
                    "TYPE_NAME": type_list["type"],
                }
                selected_type_charge_info = self.db.select_one("TYPE_CHARGE_LIST", "TYPE_CHARGE_ID", type_charge_select_condition)
                selected_type_charge_ID = selected_type_charge_info["TYPE_CHARGE_ID"]
                for item_element in type_list['type_list']:
                    item_charge_dict = {
                        "TYPE_CHARGE_ID": selected_type_charge_ID,
                        "ITEM_NAME": item_element["name"],
                        "ITEM_REGION": item_element["region"],
                        "ITEM_USE_AMT": item_element["use_amt"],
                        "ITEM_PAY_AMT": item_element["pay_amt"],
                        "ITEM_USER_PAY_AMT": item_element["pay_amt"],
                        "ITEM_START_DATE": item_element["start_date"],
                    }
                    item_charge_list.append(item_charge_dict)
        return item_charge_list


    def service_charge_list_update(self):
        """
        서비스 사용 요금 목록을 데이터베이스에 업데이트합니다.

        각 클라우드 요소에 대해 청구 월별로 서비스 요금 정보를 가져오고, SERVICE_CHARGE_LIST와 ITEM_CHARGE_LIST 테이블에 삽입 또는 업데이트합니다.
        """
        current_cloud_list = self.db.select_many("CLOUD_LIST", None)
        for cloud_element in current_cloud_list:
            period_list = self.generate_month_range(cloud_element["START_DATE"], self.end_date)
            for bill_month in period_list:
                total_charge_select_condition = {"CLOUD_ID": cloud_element["CLOUD_ID"], "BILL_MONTH": bill_month}
                total_charge_info = self.db.select_one("TOTAL_CHARGE_LIST", None, total_charge_select_condition)
                if not total_charge_info:
                    continue
                else:
                    total_charge_id = total_charge_info['TOTAL_CHARGE_ID']
                    total_cloud_charge_select_condition = {"TOTAL_CHARGE_ID": total_charge_id}
                    total_cloud_charge_info = self.db.select_one("TOTAL_CLOUD_CHARGE_LIST", None, total_cloud_charge_select_condition)
                    service_charge_select_condition = {"TOTAL_CHARGE_CLOUD_ID": total_cloud_charge_info["TOTAL_CHARGE_CLOUD_ID"]}
                    current_service_charge_list = self.db.select_many("CHARGE_CLOUD_SERVICE_LIST", None, service_charge_select_condition)
                if not current_service_charge_list:
                    service_charge_list, service_charge_api = self.service_charge_info_api(cloud_element, total_cloud_charge_info,bill_month)
                    for service_charge_dict in service_charge_list:
                        self.db.insert("CHARGE_CLOUD_SERVICE_LIST", service_charge_dict)
                    type_charge_list,service_charge_api = self.type_charge_info_api(service_charge_api)
                    for type_charge_dict in type_charge_list:
                        self.db.insert("TYPE_CHARGE_LIST", type_charge_dict)

                    item_charge_list = self.item_charge_info_api(service_charge_api)
                    for item_charge_dict in item_charge_list:
                        self.db.insert("ITEM_CHARGE_LIST", item_charge_dict)

                elif bill_month == self.end_date:
                    service_charge_list, service_charge_api = self.service_charge_info_api(cloud_element, total_cloud_charge_info,bill_month)
                    for service_charge_element in service_charge_list:
                        service_charge_condition = {
                            "TOTAL_CHARGE_CLOUD_ID": service_charge_element["TOTAL_CHARGE_CLOUD_ID"],
                            "CLOUD_SERVICE_CHARGE_CODE": service_charge_element["CLOUD_SERVICE_CHARGE_CODE"],
                        }
                        self.db.update("CHARGE_CLOUD_SERVICE_LIST", service_charge_element, service_charge_condition)

                    type_charge_list,service_charge_api = self.type_charge_info_api(service_charge_api)
                    for type_charge_element in type_charge_list:
                        type_charge_update_condition = {
                                "CLOUD_SERVICE_CHARGE_ID": type_charge_element["CLOUD_SERVICE_CHARGE_ID"],
                                "TYPE_NAME": type_charge_element["TYPE_NAME"],
                            }
                        self.db.update("TYPE_CHARGE_LIST", type_charge_element, type_charge_update_condition)

                    item_charge_list = self.item_charge_info_api(service_charge_api)
                    for item_charge_element in item_charge_list:
                        item_charge_update_condition = {
                                "TYPE_CHARGE_ID": item_charge_element["TYPE_CHARGE_ID"],
                                "ITEM_NAME": item_charge_element["ITEM_NAME"],
                                "ITEM_REGION": item_charge_element["ITEM_REGION"],
                            }
                        self.db.update("ITEM_CHARGE_LIST", item_charge_element, item_charge_update_condition)

    def update_database(self):
        """
        데이터베이스 업데이트를 수행하는 메서드입니다.

        서비스 목록, 총 사용 요금 목록, 서비스 사용 요금 목록을 업데이트하고, 데이터베이스 연결을 종료합니다.
        """
        logging.basicConfig(filename='data_setting/scheduler_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

        self.service_list_update()
        self.total_charge_list_update()
        self.service_charge_list_update()
        self.db.close()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"데이터 업데이트가 완료되었습니다. 현재 시간: {current_time}")

if __name__ == "__main__":
    db = MySQLDatabase()

    database_updater = BillingDatabaseUpdater()
    database_updater.create_database_from_sql()
    db.delete("ITEM_CHARGE_LIST")
    db.delete("TYPE_CHARGE_LIST")
    db.delete("CHARGE_CLOUD_SERVICE_LIST")
    db.delete("CHARGE_THIRD_PARTY_LIST")
    db.delete("CHARGE_MANAGED_SERVICE_LIST")
    db.delete("CHARGE_OTHER_SERVICE_LIST")
    db.delete("CHARGE_CLOUD_SERVICE_LIST")
    db.delete("TOTAL_CLOUD_CHARGE_LIST")
    db.delete("TOTAL_CHARGE_THIRD_PARTY_LIST")
    db.delete("TOTAL_CHARGE_MANAGED_SERVICE_LIST")
    db.delete("TOTAL_CHARGE_OTHER_SERVICE_LIST")
    db.delete("TOTAL_CHARGE_LIST")
    db.delete("SERVICE_LIST")
    db.delete("THIRD_PARTY_LIST")
    db.delete("MANAGED_SERVICE_LIST")
    db.delete("OTHER_SERVICE_LIST")
    db.delete("CLOUD_LIST")
    db.delete("USER_LIST")

    database_updater.user_list_insert()
    database_updater.update_database()