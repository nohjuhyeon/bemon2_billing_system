import mysql.connector
import os 

def create_database_from_sql(file_path, host, port, user, password, database):
    # MySQL 데이터베이스에 연결
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password
    )

    cursor = connection.cursor()

    # 데이터베이스 생성
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    cursor.execute(f"USE {database}")

    # SQL 파일 읽기
    with open(file_path, 'r', encoding='utf-8-sig') as file:
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

# 사용 예시
create_database_from_sql(
    file_path='bemon2.sql',
    host=os.environ.get("MYSQL_HOST"),
    port=os.environ.get("MYSQL_PORT"),
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PASSWORD"),
    database=os.environ.get("MYSQL_DATABASE")
)
