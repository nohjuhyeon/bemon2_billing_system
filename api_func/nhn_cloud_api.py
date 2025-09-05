from datetime import datetime, timedelta
import os
import requests
import base64
import json

class NhnCloudApi:
    """
    NHN 클라우드 API를 호출하여 토큰 생성, 조회 및 삭제 기능을 제공하는 클래스.

    Attributes:
        url (str): NHN 클라우드 API의 기본 URL.
        user_access_key_id (str): API 호출을 위한 사용자 액세스 키 ID.
        secret_access_key (str): API 호출을 위한 시크릿 액세스 키.

    주요 기능:
        1. 토큰 생성 (token_create):
            - 사용자 액세스 키와 시크릿 키를 사용하여 인증 토큰을 생성.
        2. 토큰 조회 (check_token):
            - 발급된 토큰의 상태를 확인하고 조회.
        3. 토큰 삭제 (delete_tokens):
            - 특정 사용자 액세스 키와 토큰 ID를 사용하여 토큰을 만료.
    """

    def __init__(self, api_type):
        """
        NhnCloudApi 클래스의 초기화 메서드.

        Args:
            api_type (str): API 타입 ('공공' 또는 '민간').
        
        Variables:
            url (str): NHN 클라우드 API의 기본 URL.
            user_access_key_id (str): API 호출을 위한 사용자 액세스 키 ID.
            secret_access_key (str): API 호출을 위한 시크릿 액세스 키.

        주요 작업:
            1. API 타입에 따라 기본 URL과 사용자 액세스 키, 시크릿 키를 설정.
            2. 환경 변수에서 액세스 키와 시크릿 키를 가져옴.
        """
        if api_type == '공공':
            self.url = "https://oauth.api.nhncloudservice.com/oauth2/token/create"
            self.user_access_key_id = os.environ.get("NHN_CLOUD_API_KEY")
            self.secret_access_key = os.environ.get("NHN_CLOUD_SECRET_KEY")
        elif api_type == '민간':
            self.url = "https://oauth.api.nhncloudservice.com/oauth2/token/create"
            self.user_access_key_id = os.environ.get("NHN_CLOUD_API_KEY")
            self.secret_access_key = os.environ.get("NHN_CLOUD_SECRET_KEY")

    def token_create(self):
        """
        사용자 액세스 키와 시크릿 키를 사용하여 인증 토큰을 생성하는 메서드.

        Returns:
            token (str): 생성된 인증 토큰(access_token).

        Variables:
            credentials (str): 사용자 액세스 키와 시크릿 키를 결합한 문자열.
            encoded_credentials (str): Base64로 인코딩된 인증 정보.
            headers (dict): API 요청 헤더.
            data (dict): API 요청 바디.
            response (requests.Response): HTTP 응답 객체.

        주요 작업:
            1. 사용자 액세스 키와 시크릿 키를 결합하여 Base64로 인코딩.
            2. 헤더와 요청 바디를 구성하여 POST 요청을 전송.
            3. 응답 결과를 처리하여 인증 토큰을 반환.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - ValueError: 데이터 처리 중 오류가 발생할 경우 처리.
            - requests.RequestException: 네트워크 오류가 발생할 경우 처리.
            - TimeoutError: 요청이 시간 초과되었을 경우 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            # Base64 인코딩
            credentials = f"{self.user_access_key_id}:{self.secret_access_key}"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

            # 요청 헤더
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            }

            # 요청 바디
            data = {"grant_type": "client_credentials"}

            # POST 요청
            response = requests.post(self.url, headers=headers, data=data)

            # 응답 결과 처리
            if response.status_code == 200:
                token = response.json().get("access_token")  # access_token 반환
                return token
            else:
                raise("토큰 발급을 실패하였습니다.")
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except ValueError as e:
            raise (f"데이터 처리 중 오류가 발생했습니다: {e}")  
        except requests.RequestException as e:
            raise (f"네트워크 오류가 발생했습니다: {e}")
        except TimeoutError as e:
            raise (f"요청이 시간 초과되었습니다: {e}")
        except Exception as e:
            raise (f"토큰 발급 중 오류가 발생했습니다: {e}")

    def check_token(self):
        """
        발급된 토큰의 상태를 조회하는 메서드.

        Returns:
            response_result (dict): 토큰 상태 정보를 담은 JSON 데이터.

        Variables:
            token (str): 생성된 인증 토큰.
            uri (str): API 호출 URL.
            query_params (dict): API 호출 쿼리 파라미터.
            headers (dict): API 요청 헤더.
            response (requests.Response): HTTP 응답 객체.

        주요 작업:
            1. 토큰을 생성하여 헤더에 추가.
            2. API URL과 쿼리 파라미터를 설정.
            3. GET 요청을 보내고 응답 데이터를 JSON 형식으로 반환.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - ValueError: 데이터 처리 중 오류가 발생할 경우 처리.
            - requests.RequestException: 네트워크 오류가 발생할 경우 처리.
            - TimeoutError: 요청이 시간 초과되었을 경우 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            token = self.token_create()

            # API URL 및 쿼리 파라미터
            uri = "https://core.api.nhncloudservice.com/v1/authentications/user-access-keys/{}/tokens".format(self.user_access_key_id)
            query_params = {"status": "ACTIVE"}

            # 요청 헤더
            headers = {"x-nhn-authorization": f"Bearer {token}"}  # 토큰을 적절한 형식으로 전달

            # GET 요청 보내기
            response = requests.get(uri, headers=headers, params=query_params)

            # 응답 결과 처리
            print("Status Code:", response.status_code)
            if response.status_code == 200:
                response_result = response.json()
                return response_result
            else:
                raise("API 호출 시 오류가 발생했습니다.")
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except ValueError as e:
            raise(f"데이터 처리 중 오류가 발생했습니다: {e}")
        except requests.RequestException as e:
            raise(f"네트워크 오류가 발생했습니다: {e}")
        except TimeoutError as e:
            raise(f"요청이 시간 초과되었습니다: {e}")
        except Exception as e:
            raise(f"토큰 조회 중 오류가 발생했습니다: {e}")

    def delete_tokens(self, user_access_key_id, token):
        """
        특정 사용자 액세스 키와 토큰 ID를 사용하여 토큰을 만료하는 메서드.

        Args:
            user_access_key_id (str): 사용자 액세스 키 ID.
            token (str): 인증 토큰.

        Returns:
            response_result (dict): 토큰 삭제 결과를 담은 JSON 데이터.

        Variables:
            uri (str): API 호출 URL.
            headers (dict): API 요청 헤더.
            token_ids (list): 만료시킬 토큰 ID 리스트.
            tokens (list): 만료시킬 토큰 리스트.
            body (dict): API 요청 바디.
            response (requests.Response): HTTP 응답 객체.

        주요 작업:
            1. API URL과 요청 헤더를 설정.
            2. 만료시킬 토큰 ID와 토큰 리스트를 요청 바디에 추가.
            3. DELETE 요청을 보내고 응답 데이터를 JSON 형식으로 반환.

        예외 처리:
            - KeyError: 응답 데이터에서 누락된 키가 있을 경우 발생.
            - ValueError: 데이터 처리 중 오류가 발생할 경우 처리.
            - requests.RequestException: 네트워크 오류가 발생할 경우 처리.
            - TimeoutError: 요청이 시간 초과되었을 경우 처리.
            - Exception: 기타 예기치 못한 오류에 대한 처리로, 오류 메시지를 출력하고 예외를 발생.
        """
        try:
            # API URL
            uri = f"https://core.api.nhncloudservice.com/v1/authentications/user-access-keys/{user_access_key_id}/tokens"

            # 요청 헤더
            headers = {
                "Content-Type": "application/json",  # JSON 형식의 Request Body를 전달하기 위해 Content-Type 설정
                "x-nhn-authorization": f"Bearer {token}",  # 발급받은 토큰을 헤더에 추가
            }

            # 만료시킬 토큰 ID와 토큰 목록
            token_ids = []  # 예시: 만료시킬 토큰 ID
            tokens = []  # 예시: 만료시킬 토큰

            # 요청 바디 생성
            body = {}
            if token_ids:
                body["tokenIds"] = token_ids
            if tokens:
                body["tokens"] = tokens

            # DELETE 요청 보내기
            response = requests.delete(uri, headers=headers, data=json.dumps(body))

            # 디버깅용 URL 출력
            print("Request URL:", uri)
            print("Request Body:", body)

            # 응답 결과 처리
            print("Status Code:", response.status_code)
            if response.status_code == 200:
                print("Response Body:", response.text)
                response_result  = response.json()
                return response_result
            else:
                raise("API 호출 시 오류가 발생했습니다.")
        except KeyError as e:
            raise(f"응답 데이터 형식이 예상과 다릅니다: {e}")
        except ValueError as e:
            raise(f"데이터 처리 중 오류가 발생했습니다: {e}")
        except requests.RequestException as e:
            raise(f"네트워크 오류가 발생했습니다: {e}")
        except TimeoutError as e:
            raise(f"요청이 시간 초과되었습니다: {e}")
        except Exception as e:
            raise(f"토큰 삭제 중 오류가 발생했습니다: {e}")
