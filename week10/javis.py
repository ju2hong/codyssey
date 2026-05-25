"""
javis.py - 음성 녹음 모듈
화성 생존 일지를 음성으로 기록하기 위한 마이크 인식 및 녹음 기능
"""

import os
import wave
import datetime

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
    filename = now.strftime('%Y%m%d-%H%M%S') + '.wav'
    return os.path.join(RECORDS_DIR, filename)


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

    import threading

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
        print('  3. 종료')
        print()

        choice = input('선택 > ').strip()

        if choice == '1':
            list_microphones()

        elif choice == '2':
            input_devices = list_microphones()
            device_index = select_microphone(input_devices)
            record_audio(device_index=device_index)

        elif choice == '3':
            print('\n[종료] JAVIS를 종료합니다.')
            break

        else:
            print('[경고] 1, 2, 3 중 하나를 입력하세요.')


if __name__ == '__main__':
    main()