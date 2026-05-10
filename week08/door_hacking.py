import os
import itertools
import string
import zipfile
import zlib
import multiprocessing
from datetime import datetime


ZIP_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'emergency_storage_key.zip'
)

CHARACTERS = string.digits + string.ascii_lowercase
PASSWORD_LENGTH = 6


def _try_chunk(args):
    zip_path, prefix, characters, password_length = args
    remaining = password_length - len(prefix)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            first_file = zf.namelist()[0]
            for combo in itertools.product(characters, repeat=remaining):
                password = prefix + ''.join(combo)
                try:
                    zf.read(first_file, pwd=password.encode())
                    return password
                except Exception:
                    continue
    except (FileNotFoundError, zipfile.BadZipFile, OSError):
        return None

    return None


def unlock_zip(zip_path=ZIP_PATH):
    characters = CHARACTERS
    password_length = PASSWORD_LENGTH

    start_time = datetime.now()
    cpu_count = multiprocessing.cpu_count()

    print(f'시작 시간: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'zip 파일: {zip_path}')
    print(f'비밀번호 구성: 숫자 + 소문자 알파벳 {password_length}자리')
    print(f'경우의 수: {len(characters) ** password_length:,}가지')
    print(f'사용 CPU 코어: {cpu_count}개')
    print('암호 해독을 시작합니다...\n')

    prefix_length = 2
    prefixes = [
        ''.join(p)
        for p in itertools.product(characters, repeat=prefix_length)
    ]
    total = len(prefixes)
    tasks = [
        (zip_path, prefix, characters, password_length)
        for prefix in prefixes
    ]

    completed = 0
    password = None

    try:
        with multiprocessing.Pool(processes=cpu_count) as pool:
            for result in pool.imap_unordered(_try_chunk, tasks):
                completed += 1
                elapsed = datetime.now() - start_time
                print(
                    f'\r진행: {completed}/{total} '
                    f'({completed / total * 100:.1f}%) '
                    f'| 경과: {elapsed}',
                    end='',
                    flush=True
                )
                if result is not None:
                    pool.terminate()
                    password = result
                    break

    except KeyboardInterrupt:
        print('\n\n[중단] 사용자에 의해 중단되었습니다.')
        return None

    elapsed = datetime.now() - start_time

    if password:
        print(f'\n\n[성공] zip 암호를 찾았습니다!')
        print(f'zip 암호: {password}')
        print(f'총 경과 시간: {elapsed}')

        try:
            with zipfile.ZipFile(zip_path) as zf:
                content = zf.read(zf.namelist()[0], pwd=password.encode())
            storage_key = content.decode('utf-8').strip()
            print(f'\nemergency storage key: {storage_key}')
        except Exception as e:
            print(f'키 읽기 오류: {e}')

        try:
            with open('password.txt', 'w') as f:
                f.write(password)
            print('\nzip 암호가 password.txt에 저장되었습니다.')
        except OSError as e:
            print(f'파일 저장 오류: {e}')

        return password

    print('\n암호를 찾지 못했습니다.')
    return None


if __name__ == '__main__':
    unlock_zip()