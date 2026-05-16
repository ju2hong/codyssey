def decode_text(target_text, shift):
    decoded_text = ''
    alphabet_count = 26

    for char in target_text:

        if 'A' <= char <= 'Z':
            decoded_char = chr(
                (ord(char) - ord('A') - shift) % alphabet_count
                + ord('A')
            )
            decoded_text += decoded_char

        elif 'a' <= char <= 'z':
            decoded_char = chr(
                (ord(char) - ord('a') - shift) % alphabet_count
                + ord('a')
            )
            decoded_text += decoded_char

        else:
            decoded_text += char

    return decoded_text


def caesar_cipher_decode(target_text):
    alphabet_count = 26

    print('===== 카이사르 암호 해독 결과 =====')
    print()

    for shift in range(alphabet_count):
        decoded_result = decode_text(target_text, shift)

        print(f'[이동 값 : {shift}]')
        print(decoded_result)
        print()


def save_result(target_text):
    try:
        shift_input = input(
            '정답으로 보이는 이동 값을 입력하세요 (0~25): '
        )

        shift = int(shift_input)

        if shift < 0 or shift > 25:
            print('0부터 25 사이의 숫자를 입력해야 합니다.')
            return

        final_result = decode_text(target_text, shift)

        with open(
            'result.txt',
            'w',
            encoding = 'utf-8'
        ) as file:
            file.write(final_result)

        print()
        print('===== 최종 복호화 결과 =====')
        print(final_result)
        print()
        print('result.txt 파일 저장 완료')

    except ValueError:
        print('숫자를 입력해야 합니다.')

    except OSError:
        print('result.txt 저장 중 오류가 발생했습니다.')


def main():
    try:
        with open(
            'password.txt',
            'r',
            encoding = 'utf-8'
        ) as file:
            encrypted_text = file.read().strip()

        if encrypted_text == '':
            print('password.txt 파일이 비어 있습니다.')
            return

        caesar_cipher_decode(encrypted_text)

        save_result(encrypted_text)

    except FileNotFoundError:
        print('password.txt 파일을 찾을 수 없습니다.')

    except OSError:
        print('파일을 읽는 중 오류가 발생했습니다.')


if __name__ == '__main__':
    main()