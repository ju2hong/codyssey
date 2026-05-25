import os
import wave
import datetime
import threading

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

# 녹음 설정 상수
CHUNK = 1024
FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
CHANNELS = 1
RATE = 44100
RECORDS_DIR = 'records'
DATE_FORMAT = '%Y%m%d'
DATETIME_FORMAT = '%Y%m%d-%H%M%S'


def ensure_records_dir():
    """records 폴더가 없으면 생성한다."""
    if not os.path.exists(RECORDS_DIR):
        os.makedirs(RECORDS_DIR)
        print(f'[정보] {RECORDS_DIR} 폴더를 생성했습니다.')


def get_filename():
    """현재 날짜와 시간을 기반으로 파일명을 생성한다.

    Returns:
        str: '년월일-시간분초.wav' 형식의 파일 경로
    """
    now = datetime.datetime.now()
    filename = now.strftime(DATETIME_FORMAT) + '.wav'
    return os.path.join(RECORDS_DIR, filename)


def parse_date_from_filename(filename):
    """파일명에서 날짜를 파싱한다.

    파일명 형식: '년월일-시간분초.wav' (예: 20260525-143022.wav)

    Args:
        filename (str): 파일명 (경로 제외)

    Returns:
        datetime.date or None: 파싱된 날짜, 실패 시 None
    """
    basename = os.path.splitext(filename)[0]
    parts = basename.split('-')
    if len(parts) < 2:
        return None
    try:
        return datetime.datetime.strptime(parts[0], DATE_FORMAT).date()
    except ValueError:
        return None


def input_date(prompt):
    """사용자로부터 날짜를 입력받는다.

    Args:
        prompt (str): 입력 안내 메시지

    Returns:
        datetime.date or None: 입력된 날짜, 취소 시 None
    """
    while True:
        print(prompt)
        user_input = input('날짜 입력 (YYYYMMDD, 취소: q) > ').strip()

        if user_input.lower() == 'q':
            return None

        try:
            parsed = datetime.datetime.strptime(user_input, DATE_FORMAT).date()
            return parsed
        except ValueError:
            print('[경고] 날짜 형식이 올바르지 않습니다. 예: 20260525')


def list_records_by_date_range():
    """특정 범위의 날짜에 해당하는 녹음 파일 목록을 출력한다.

    사용자로부터 시작 날짜와 종료 날짜를 입력받아
    해당 범위에 포함되는 .wav 파일을 records 폴더에서 검색하여 출력한다.
    """
    ensure_records_dir()

    print('\n[날짜 범위로 녹음 파일 검색]')
    print('-' * 40)

    start_date = input_date('시작 날짜를 입력하세요.')
    if start_date is None:
        print('[취소] 검색을 취소했습니다.')
        return

    end_date = input_date('종료 날짜를 입력하세요.')
    if end_date is None:
        print('[취소] 검색을 취소했습니다.')
        return

    if start_date > end_date:
        print('[경고] 시작 날짜가 종료 날짜보다 늦습니다. 날짜를 바꿔서 검색합니다.')
        start_date, end_date = end_date, start_date

    print(f'\n[검색 범위] {start_date.strftime(DATE_FORMAT)} ~ '
          f'{end_date.strftime(DATE_FORMAT)}')
    print('-' * 40)

    try:
        all_files = os.listdir(RECORDS_DIR)
    except OSError as e:
        print(f'[오류] records 폴더를 읽을 수 없습니다: {e}')
        return

    matched_files = []

    for filename in sorted(all_files):
        if not filename.endswith('.wav'):
            continue
        file_date = parse_date_from_filename(filename)
        if file_date is None:
            continue
        if start_date <= file_date <= end_date:
            matched_files.append((file_date, filename))

    if not matched_files:
        print('  해당 날짜 범위에 녹음 파일이 없습니다.')
    else:
        print(f'  총 {len(matched_files)}개의 파일을 찾았습니다.\n')
        for idx, (file_date, filename) in enumerate(matched_files, start=1):
            filepath = os.path.join(RECORDS_DIR, filename)
            try:
                file_size = os.path.getsize(filepath)
                size_kb = file_size / 1024
            except OSError:
                size_kb = 0.0
            date_str = file_date.strftime('%Y년 %m월 %d일')
            print(f'  {idx:3}. [{date_str}] {filename}  ({size_kb:.1f} KB)')

    print('-' * 40)


def list_microphones():
    """시스템에서 사용 가능한 마이크 목록을 출력한다.

    Returns:
        list: 사용 가능한 입력 장치 정보 목록
    """
    audio = pyaudio.PyAudio()
    device_count = audio.get_device_count()
    input_devices = []

    print('\n[마이크 목록]')
    print('-' * 40)

    for i in range(device_count):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append(device_info)
            print(f"  인덱스 {i}: {device_info['name']}")

    print('-' * 40)

    if not input_devices:
        print('  사용 가능한 마이크가 없습니다.')

    audio.terminate()
    return input_devices


def select_microphone(input_devices):
    """사용자가 마이크를 선택하도록 한다.

    Args:
        input_devices (list): 사용 가능한 입력 장치 목록

    Returns:
        int or None: 선택된 장치 인덱스, 기본 장치 사용 시 None
    """
    if not input_devices:
        return None

    if len(input_devices) == 1:
        device_info = input_devices[0]
        print(f"\n[정보] 마이크가 1개 감지되었습니다: {device_info['name']}")
        return int(device_info['index'])

    print('\n사용할 마이크 인덱스를 입력하세요 (기본값 사용 시 Enter):')
    user_input = input('> ').strip()

    if user_input == '':
        return None

    try:
        selected_index = int(user_input)
        valid_indices = [int(d['index']) for d in input_devices]
        if selected_index in valid_indices:
            return selected_index
        else:
            print('[경고] 유효하지 않은 인덱스입니다. 기본 마이크를 사용합니다.')
            return None
    except ValueError:
        print('[경고] 숫자를 입력해야 합니다. 기본 마이크를 사용합니다.')
        return None


def record_audio(device_index=None):
    """마이크로부터 음성을 녹음하고 파일로 저장한다.

    Args:
        device_index (int or None): 사용할 마이크 인덱스.
                                    None이면 기본 장치를 사용한다.

    Returns:
        str or None: 저장된 파일 경로, 실패 시 None
    """
    ensure_records_dir()

    audio = pyaudio.PyAudio()
    filepath = get_filename()

    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
    except OSError as e:
        print(f'[오류] 마이크를 열 수 없습니다: {e}')
        audio.terminate()
        return None

    print('\n[녹음 시작] 엔터(Enter) 키를 누르면 녹음이 중지됩니다...')

    frames = []
    recording = True

    def stop_on_enter():
        nonlocal recording
        input()
        recording = False

    stop_thread = threading.Thread(target=stop_on_enter, daemon=True)
    stop_thread.start()

    while recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except OSError as e:
            print(f'[오류] 녹음 중 오류 발생: {e}')
            break

    print('[녹음 중지] 파일을 저장하는 중...')

    stream.stop_stream()
    stream.close()
    audio.terminate()

    try:
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f'[저장 완료] 파일: {filepath}')
        return filepath
    except Exception as e:
        print(f'[오류] 파일 저장 실패: {e}')
        return None


def check_pyaudio():
    """pyaudio 라이브러리 설치 여부를 확인한다.

    Returns:
        bool: 설치되어 있으면 True, 아니면 False
    """
    if not PYAUDIO_AVAILABLE:
        print('[오류] pyaudio 라이브러리가 설치되어 있지 않습니다.')
        print('       설치 명령: pip install pyaudio')
        return False
    return True


def main():
    """메인 실행 함수."""
    print('=' * 40)
    print('   JAVIS - 음성 녹음 시스템')
    print('   화성 생존 일지 음성 기록기')
    print('=' * 40)

    if not check_pyaudio():
        return

    while True:
        print('\n[메뉴]')
        print('  1. 마이크 목록 확인')
        print('  2. 음성 녹음 시작')
        print('  3. 날짜 범위로 녹음 파일 검색')
        print('  4. 종료')
        print()

        choice = input('선택 > ').strip()

        if choice == '1':
            list_microphones()

        elif choice == '2':
            input_devices = list_microphones()
            device_index = select_microphone(input_devices)
            record_audio(device_index=device_index)

        elif choice == '3':
            list_records_by_date_range()

        elif choice == '4':
            print('\n[종료] JAVIS를 종료합니다.')
            break

        else:
            print('[경고] 1, 2, 3, 4 중 하나를 입력하세요.')


if __name__ == '__main__':
    main()