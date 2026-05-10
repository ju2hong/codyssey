import os
import itertools
import string
import zipfile
import zlib
from datetime import datetime

ZIP_PATH = os.path.join(
    os.path.dirname(__file__),
    'emergency_storage_key.zip'
)

CHARACTERS = string.digits + string.ascii_lowercase
PASSWORD_LENGTH = 6
LOG_INTERVAL = 100_000


def print_progress(count, start_time, password):
    elapsed = datetime.now() - start_time

    print(
        f'반복 횟수: {count:,} | '
        f'경과 시간: {elapsed} | '
        f'현재 시도: {password}'
    )


def save_password(password):
    try:
        with open('password.txt', 'w', encoding='utf-8') as file:
            file.write(password)

        print('\nzip 암호가 password.txt에 저장되었습니다.')

    except OSError as error:
        print(f'파일 저장 오류: {error}')


def try_password(zip_file, file_name, password):
    try:
        zip_file.setpassword(password.encode())

        # 전체 파일 읽지 않고 1바이트만 읽어서 검사
        with zip_file.open(file_name) as file:
            file.read(1)

        return True

    except (
        RuntimeError,
        zlib.error,
        zipfile.BadZipFile,
        EOFError
    ):
        return False


def print_success(password, count, elapsed, storage_key):
    print('\n[성공] zip 암호를 찾았습니다!')
    print(f'zip 암호: {password}')
    print(f'총 반복 횟수: {count:,}')
    print(f'총 경과 시간: {elapsed}')
    print(f'\nemergency storage key: {storage_key}')


def unlock_zip(zip_path=ZIP_PATH):
    start_time = datetime.now()

    print(f'시작 시간: {start_time:%Y-%m-%d %H:%M:%S}')
    print(f'zip 파일: {zip_path}')
    print(
        f'비밀번호 구성: 숫자 + 소문자 알파벳 '
        f'{PASSWORD_LENGTH}자리'
    )
    print(
        f'경우의 수: '
        f'{len(CHARACTERS) ** PASSWORD_LENGTH:,}가지'
    )
    print('암호 해독을 시작합니다...\n')

    count = 0

    try:
        with zipfile.ZipFile(zip_path) as zip_file:

            file_name = zip_file.namelist()[0]

            for combination in itertools.product(
                CHARACTERS,
                repeat=PASSWORD_LENGTH
            ):
                password = ''.join(combination)
                count += 1

                if count % LOG_INTERVAL == 0:
                    print_progress(
                        count,
                        start_time,
                        password
                    )

                if not try_password(
                    zip_file,
                    file_name,
                    password
                ):
                    continue

                elapsed = datetime.now() - start_time

                zip_file.setpassword(password.encode())

                with zip_file.open(file_name) as file:
                    content = file.read()

                storage_key = content.decode(
                    'utf-8'
                ).strip()

                print_success(
                    password,
                    count,
                    elapsed,
                    storage_key
                )

                save_password(password)

                return password

    except FileNotFoundError:
        print(f'오류: {zip_path} 파일을 찾을 수 없습니다.')

    except zipfile.BadZipFile:
        print(
            f'오류: {zip_path}는 '
            f'유효한 zip 파일이 아닙니다.'
        )

    except OSError as error:
        print(f'파일 접근 오류: {error}')

    print('암호를 찾지 못했습니다.')

    return None


if __name__ == '__main__':
    unlock_zip()