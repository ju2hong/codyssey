"""
mars_weather_summary.py

화성 날씨 CSV 파일을 읽어 MySQL에 저장한다.
"""

import csv

from mysql_helper import MySQLHelper


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

    helper = MySQLHelper(
        HOST,
        PORT,
        USER,
        PASSWORD
    )

    helper.execute(
        f'CREATE DATABASE IF NOT EXISTS {DATABASE}'
    )


def create_table():
    """테이블 생성"""

    helper = MySQLHelper(
        HOST,
        PORT,
        USER,
        PASSWORD,
        DATABASE
    )

    helper.execute(
        '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT PRIMARY KEY,
            mars_date DATE NOT NULL,
            temp DECIMAL(5, 2),
            storm INT
        )
        '''
    )


def read_weather_csv():
    """CSV 읽기"""

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


def insert_weather_data(weather_data):
    """데이터 저장"""

    helper = MySQLHelper(
        HOST,
        PORT,
        USER,
        PASSWORD,
        DATABASE
    )

    query = '''
        INSERT IGNORE INTO mars_weather (
            weather_id,
            mars_date,
            temp,
            storm
        )
        VALUES (
            %s,
            %s,
            %s,
            %s
        )
    '''

    count = helper.executemany(
        query,
        weather_data
    )

    print(f'{count}건 저장 완료')


def main():

    create_database()

    create_table()

    weather_data = read_weather_csv()

    print(
        f'총 데이터 수 : {len(weather_data)}'
    )

    insert_weather_data(
        weather_data
    )

    print('작업 완료')


if __name__ == '__main__':
    main()