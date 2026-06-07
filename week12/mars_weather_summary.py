"""
mars_weather_summary.py

화성 날씨 CSV 파일을 읽어 MySQL 데이터베이스에 저장한다.
"""

import csv

import mysql.connector


CSV_FILE = 'mars_weathers_data.CSV'


def load_env():
    """.env 파일 읽기"""

    env = {}

    with open('.env', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith('#'):
                continue

            key, value = line.split('=', 1)
            env[key] = value

    return env


ENV = load_env()

HOST = ENV['DB_HOST']
PORT = int(ENV['DB_PORT'])
USER = ENV['DB_USER']
PASSWORD = ENV['DB_PASSWORD']
DATABASE = ENV['DB_NAME']


def create_database():
    """데이터베이스 생성"""

    connection = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD
    )

    cursor = connection.cursor()

    cursor.execute(
        f'CREATE DATABASE IF NOT EXISTS {DATABASE}'
    )

    cursor.close()
    connection.close()


def connect_database():
    """데이터베이스 연결"""

    return mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )


def create_table(connection):
    """테이블 생성"""

    query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT PRIMARY KEY,
            mars_date DATE NOT NULL,
            temp DECIMAL(5, 2),
            storm INT
        )
    '''

    cursor = connection.cursor()

    cursor.execute(query)

    connection.commit()

    cursor.close()


def read_weather_csv():
    """CSV 파일 읽기"""

    weather_data = []

    with open(CSV_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            weather_data.append(
                (
                    int(row['weather_id']),
                    row['mars_date'],
                    float(row['temp']),
                    int(row['storm'])
                )
            )

    return weather_data


def print_weather_data(weather_data):
    """CSV 데이터 출력"""

    print('===== CSV 데이터 확인 =====')

    for row in weather_data[:5]:
        print(row)

    print(f'총 데이터 수 : {len(weather_data)}')


def insert_weather_data(connection, weather_data):
    """데이터 저장"""

    query = '''
        INSERT IGNORE INTO mars_weather
        (
            weather_id,
            mars_date,
            temp,
            storm
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
    '''

    cursor = connection.cursor()

    cursor.executemany(
        query,
        weather_data
    )

    connection.commit()

    print(
        f'{cursor.rowcount}건 저장 완료'
    )

    cursor.close()


def main():
    """메인 함수"""

    connection = None

    try:
        create_database()

        connection = connect_database()

        create_table(connection)

        weather_data = read_weather_csv()

        print_weather_data(
            weather_data
        )

        insert_weather_data(
            connection,
            weather_data
        )

        print('작업 완료')

    except Exception as error:
        print(f'오류 발생 : {error}')

    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    main()