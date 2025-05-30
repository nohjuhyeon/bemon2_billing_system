import base64
import requests
import os
import json  # JSON 파싱을 위한 모듈


def token_create(user_access_key_id, secret_access_key):
    # Base64 인코딩
    credentials = f"{user_access_key_id}:{secret_access_key}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    # 요청 URL
    url = "https://oauth.api.nhncloudservice.com/oauth2/token/create"

    # 요청 헤더
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    # 요청 바디
    data = {"grant_type": "client_credentials"}

    # POST 요청
    response = requests.post(url, headers=headers, data=data)

    # 응답 결과 처리
    if response.status_code == 200:
        token = response.json().get("access_token")  # access_token 반환

        # .env 파일 업데이트
        update_env_file("NHN_CLOUD_ACCESS_TOKEN", token)
        return token
    else:
        print("토큰 발급 실패.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None


# .env 파일 업데이트 함수
def update_env_file(key, value, env_file_path=".env"):
    """
    .env 파일에서 지정된 키를 업데이트하거나 추가합니다.
    """
    lines = []
    updated = False

    # .env 파일 읽기
    if os.path.exists(env_file_path):
        with open(env_file_path, "r") as file:
            lines = file.readlines()

    # 기존 키 업데이트
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            updated = True

    # 키가 없으면 추가
    if not updated:
        lines.append(f"{key}={value}\n")

    # .env 파일 쓰기
    with open(env_file_path, "w") as file:
        file.writelines(lines)


# API 호출 함수
def check_token(access_key, token):
    if not token:
        print("토큰이 없습니다. API 호출을 중단합니다.")
        return None

    # API URL 및 쿼리 파라미터
    uri = "https://core.api.nhncloudservice.com/v1/authentications/user-access-keys/{}/tokens".format(
        access_key
    )
    query_params = {"status": "ACTIVE"}

    # 요청 헤더
    headers = {"x-nhn-authorization": f"Bearer {token}"}  # 토큰을 적절한 형식으로 전달

    # GET 요청 보내기
    response = requests.get(uri, headers=headers, params=query_params)

    # 디버깅용 URL 출력
    response_url = (
        requests.Request("GET", uri, headers=headers, params=query_params).prepare().url
    )

    # 응답 결과 처리
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        return response.json()  # JSON 데이터를 반환
    else:
        print("Error occurred while calling the API.")
        print("Response:", response.text)
        return None


# DELETE 요청을 보내는 함수
def delete_tokens(user_access_key_id, token):
    if not token:
        print("토큰이 없습니다. API 호출을 중단합니다.")
        return None

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
        return response.json()  # JSON 데이터를 반환
    else:
        print("Error occurred while calling the API.")
        print("Response:", response.text)
        return None


# Main 실행
if __name__ == "__main__":
    user_access_key_id = os.getenv("NHN_CLOUD_API_KEY")
    secret_access_key = os.getenv("NHN_CLOUD_SECRET_KEY")
    token = os.getenv("NHN_CLOUD_ACCESS_TOKEN")
    # 환경 변수 확인
    if not user_access_key_id or not secret_access_key:
        print("API Key 또는 Secret Key가 설정되지 않았습니다. 환경 변수를 확인하세요.")
        exit()

    # 토큰 확인
    token_check_list = check_token(user_access_key_id, token)
    if token_check_list["header"]["resultMessage"] == "Token is not valid":
        # 토큰 생성
        token = token_create(user_access_key_id, secret_access_key)
        print("Generated Token:", token)

    elif token_check_list["header"]["resultMessage"] == "SUCCESS":
        print("token is valid")
        print([i["tokenId"] for i in token_check_list["tokens"]])
    # API 호출
    # response_data = delete_tokens(user_access_key_id, token)
    # if response_data:
    #     # JSON 데이터를 dict로 출력
    #     print("Parsed Data:", response_data)
    # else:
    #     print("API 응답 데이터가 없습니다.")
