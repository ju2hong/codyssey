# 설치가 잘 되었는지 확인을 위해 출력합니다.
# print("Hello Mars")

def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
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

def print_logs_reverse(log_lines):
    print("=== 로그 시간 역순 출력 ===")

    header = log_lines[0]
    data_logs = log_lines[1:]

    print(header.strip())

    for line in reversed(data_logs):
        print(line.strip())

def extract_problem_logs(log_lines):
    problem_logs = []

    abnormal_keywords = [
        "unstable",
        "explosion"
    ]

    for line in log_lines:
        lower_line = line.lower()

        if any(keyword in lower_line for keyword in abnormal_keywords):
            problem_logs.append(line)

    return problem_logs

def save_problem_logs(problem_logs, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            for log in problem_logs:
                file.write(log)

        print("문제 로그가 problem_logs.log 파일로 저장되었습니다.")

    except Exception as error:
        print("문제 로그 저장 중 오류 발생")
        print(error)


def main():
    log_file_path = 'week01/mission_computer_main.log'
    output_file_path = 'week01/problem_logs.log'

    log_lines = read_log_file(log_file_path)

    if not log_lines:
        return

    print_logs_reverse(log_lines)

    problem_logs = extract_problem_logs(log_lines)

    save_problem_logs(problem_logs, output_file_path)


if __name__ == '__main__':
    main()