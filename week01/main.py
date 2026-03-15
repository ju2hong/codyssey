# 설치가 잘 되었는지 확인을 위해 출력합니다.
# print("Hello Mars")

def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding = 'utf-8') as file:
            return file.readlines()

    except FileNotFoundError:
        print('로그 파일을 찾을 수 없습니다.')
        return []

    except PermissionError:
        print('로그 파일을 읽을 권한이 없습니다.')
        return []

    except Exception as error:
        print('파일 처리 중 오류가 발생했습니다.')
        print(error)
        return []


def print_log_contents(log_lines):
    for line in log_lines:
        print(line.strip())


def main():
    log_file_path = 'week01/mission_computer_main.log'
    log_lines = read_log_file(log_file_path)
    print_log_contents(log_lines)


if __name__ == '__main__':
    main()