import pickle
import config


def read_csv_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print('파일을 찾을 수 없습니다.')
    except Exception as e:
        print('파일 읽기 오류:', e)

    return []


def parse_csv(lines):
    data_list = []

    for line in lines[1:]:

        if not line.strip():
            continue

        values = line.strip().split(',')

        if len(values) != 5:
            print('컬럼 오류:', line)
            continue

        try:
            flammability = float(values[4])
        except ValueError:
            print('Flammability 변환 실패:', line)
            continue

        try:
            weight = float(values[1])
        except ValueError:
            weight = None

        try:
            gravity = float(values[2])
        except ValueError:
            gravity = None

        data = {
            'Substance': values[0],
            'Weight': weight,
            'Specific Gravity': gravity,
            'Strength': values[3],
            'Flammability': flammability
        }

        data_list.append(data)

    return data_list


def sort_by_flammability(data_list):
    return sorted(
        data_list,
        key=lambda x: x['Flammability'],
        reverse=True
    )


def filter_dangerous(data_list):
    return [
        item for item in data_list
        if item['Flammability'] >= config.FLAMMABILITY_THRESHOLD
    ]


def save_to_csv(file_path, data_list):
    try:
        with open(file_path, 'w') as file:
            file.write('Substance,Weight,Specific Gravity,Strength,Flammability\n')

            for item in data_list:
                line = (
                    f"{item['Substance']},"
                    f"{item['Weight']},"
                    f"{item['Specific Gravity']},"
                    f"{item['Strength']},"
                    f"{item['Flammability']}\n"
                )
                file.write(line)

        print('CSV 저장 완료')

    except Exception as e:
        print('CSV 저장 오류:', e)


# 이진 파일 저장
def save_to_binary(file_path, data_list):
    try:
        with open(file_path, 'wb') as file:
            pickle.dump(data_list, file)

        print('이진 파일 저장 완료')

    except Exception as e:
        print('이진 파일 저장 오류:', e)


# 이진 파일 읽기
def read_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)

        print('\n=== 이진 파일 복원 데이터 ===')
        for item in data:
            print(item)

    except Exception as e:
        print('이진 파일 읽기 오류:', e)
        

def main():
    lines = read_csv_file(config.INPUT_FILE)
    if not lines:
        return

    data_list = parse_csv(lines)

    sorted_list = sort_by_flammability(data_list)

    dangerous_list = filter_dangerous(sorted_list)

    save_to_csv(config.OUTPUT_FILE, dangerous_list)

    # 보너스
    save_to_binary(config.BINARY_FILE, sorted_list)
    read_binary(config.BINARY_FILE)

if __name__ == '__main__':
    main()