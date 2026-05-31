import csv
import os
 
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
 
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
 
# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
 
RECORDS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'week10', 'records'
)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SEP = '-' * 40
 
# ---------------------------------------------------------------------------
# STT (Speech to Text) - whisper 기반
# ---------------------------------------------------------------------------
 
 
def get_record_files():
    """RECORDS_DIR 내 음성 파일 목록을 반환한다."""
    try:
        all_files = sorted(os.listdir(RECORDS_DIR))
    except OSError as e:
        print(f'[오류] records 폴더를 읽을 수 없습니다: {e}')
        return []
    return [
        f for f in all_files
        if f.endswith(('.wav', '.mp3', '.m4a'))
    ]
 
 
def convert_audio_to_text(model, audio_path):
    """whisper 모델로 음성 파일을 텍스트로 변환하고 세그먼트를 반환한다."""
    result = model.transcribe(audio_path, language='ko')
    return result.get('segments', [])
 
 
def save_csv(audio_path, segments):
    """세그먼트 결과를 CSV 파일로 저장한다."""
    audio_name = os.path.splitext(os.path.basename(audio_path))[0]
    csv_path = os.path.join(CURRENT_DIR, audio_name + '.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['음성 파일내에서의 시간', '인식된 텍스트'])
        for segment in segments:
            writer.writerow([
                round(segment['start'], 2),
                segment['text'].strip()
            ])
 
 
def run_stt():
    """STT 메뉴 진입점: 파일 목록 표시 → 선택 → whisper 변환 → CSV 저장."""
    if not WHISPER_AVAILABLE:
        print('[오류] whisper가 설치되어 있지 않습니다. (pip install openai-whisper)')
        return
 
    audio_files = get_record_files()
    if not audio_files:
        print('[안내] 변환할 음성 파일이 없습니다.')
        return
 
    print(f'\n[녹음 파일 목록]\n{SEP}')
    for idx, f in enumerate(audio_files, start=1):
        size_kb = os.path.getsize(os.path.join(RECORDS_DIR, f)) / 1024
        print(f'  {idx:3}. {f}  ({size_kb:.1f} KB)')
    print(SEP)
 
    while True:
        user_input = input(
            f'변환할 파일 번호 입력 (1~{len(audio_files)}, 취소: q) > '
        ).strip()
        if user_input.lower() == 'q':
            print('[취소] STT 변환을 취소했습니다.')
            return
        try:
            num = int(user_input)
            if 1 <= num <= len(audio_files):
                selected = audio_files[num - 1]
                break
            print(f'[경고] 1~{len(audio_files)} 사이의 번호를 입력하세요.')
        except ValueError:
            print('[경고] 숫자 또는 q를 입력하세요.')
 
    audio_path = os.path.join(RECORDS_DIR, selected)
    print(f'\n[STT 시작] {selected}')
    model = whisper.load_model('base')
    segments = convert_audio_to_text(model, audio_path)
    save_csv(audio_path, segments)
    print(f'[저장 완료] {os.path.splitext(selected)[0]}.csv')
 
 
# ---------------------------------------------------------------------------
# 키워드 검색
# ---------------------------------------------------------------------------
 
 
def get_csv_files():
    """현재 폴더 내 CSV 파일 목록을 반환한다."""
    all_files = sorted(os.listdir(CURRENT_DIR))
    return [f for f in all_files if f.endswith('.csv')]
 
 
def search_keyword():
    """CSV 파일에서 키워드를 검색하고 결과를 출력한다."""
    csv_files = get_csv_files()
    if not csv_files:
        print('[안내] 검색할 CSV 파일이 없습니다.')
        return
 
    keyword = input('검색할 키워드 입력 > ').strip()
    if not keyword:
        print('[경고] 키워드를 입력하세요.')
        return
 
    print(f'\n[검색 결과] 키워드: {keyword}\n{SEP}')
    total = 0
 
    for csv_file in csv_files:
        csv_path = os.path.join(CURRENT_DIR, csv_file)
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # 헤더 건너뜀
            for row in reader:
                if len(row) < 2:
                    continue
                if keyword in row[1]:
                    print(f'  [{csv_file}]  {row[0]}초  {row[1]}')
                    total += 1
 
    if total == 0:
        print('  일치하는 내용이 없습니다.')
    else:
        print(f'{SEP}\n  총 {total}개 결과')
 
 
# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------
 
 
def print_menu():
    """메뉴 항목을 출력한다."""
    print('\n[메뉴]')
    print('  1. 음성 → 텍스트 변환 (STT)')
    print('  2. 키워드 검색')
    print('  3. 종료')
    print()
 
 
def main():
    """메인 실행 함수."""
    print('=' * 40)
    print('   JAVIS - STT 시스템')
    print('   화성 생존 일지 음성 기록기')
    print('=' * 40)
 
    while True:
        print_menu()
        choice = input('선택 > ').strip()
 
        if choice == '1':
            run_stt()
 
        elif choice == '2':
            search_keyword()
 
        elif choice == '3':
            print('\n[종료] JAVIS를 종료합니다.')
            break
 
        else:
            print('[경고] 1, 2, 3 중 하나를 입력하세요.')
 
 
if __name__ == '__main__':
    main()
