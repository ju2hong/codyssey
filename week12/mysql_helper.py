"""
mysql_helper.py

MySQL 데이터베이스 연결 및 쿼리 실행을 담당한다.
"""

import mysql.connector


class MySQLHelper:

    def __init__(
        self,
        host,
        port,
        user,
        password,
        database=None
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def get_connection(self):
        """DB 연결 반환"""

        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def execute(self, query):
        """단일 쿼리 실행"""

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.execute(query)

        connection.commit()

        cursor.close()
        connection.close()

    def executemany(self, query, data):
        """여러 건의 데이터 저장"""

        connection = self.get_connection()

        cursor = connection.cursor()

        cursor.executemany(
            query,
            data
        )

        connection.commit()

        count = cursor.rowcount

        cursor.close()
        connection.close()

        return count