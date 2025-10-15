import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 1. 설정 파일 로드
def load_config(file_path):
    """JSON 설정 파일을 로드합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"오류: 설정 파일 '{file_path}'을 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError:
        print(f"오류: 설정 파일 '{file_path}'의 JSON 형식이 잘못되었습니다.")
        return None

# 2. 이메일 발송
def send_email(config, sender_password):
    """자동 이메일을 발송합니다."""
    if not config:
        return

    # 환경 변수에서 SMTP 비밀번호 가져오기 (GitHub Secrets 사용 권장)
    if not sender_password:
        print("오류: 발신자 비밀번호가 설정되지 않았습니다.")
        return

    # SMTP 서버 정보
    smtp_server = config['smtp_server']
    smtp_port = config['smtp_port']
    sender_email = config['sender_email']
    receiver_email = config['receiver_email']
    subject = config['email_subject']
    
    # 이메일 내용 (현재 시간 포함)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = f"안녕하세요.\n\n이 메일은 GitHub Actions를 통해 {current_time}에 자동 발송된 테스트 이메일입니다.\n\n자동화 프로세스가 성공적으로 실행되었습니다."

    # MIME 객체 생성
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    
    # 본문 추가
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # 메일 전송
    try:
        print(f"{smtp_server}:{smtp_port}에 연결 중...")
        # SMTP_SSL을 사용하거나, SMTP + starttls를 사용
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() # 보안 연결 시작
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("이메일이 성공적으로 발송되었습니다!")
        return True
    except Exception as e:
        print(f"오류 발생: 이메일 전송 실패 - {e}")
        return False

# 3. 결과 저장 (.txt 파일)
def save_result(file_path, success):
    """이메일 발송 결과를 파일에 저장합니다."""
    status = "성공" if success else "실패"
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 이메일 발송: {status}\n"
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    print(f"결과가 '{file_path}'에 저장되었습니다.")

if __name__ == "__main__":
    # 설정 파일 경로
    CONFIG_FILE = 'email_config.json'
    # 결과 저장 파일 경로
    RESULT_FILE = 'email_log.txt'
    
    # 환경 변수에서 비밀번호 로드 (GitHub Actions의 Secrets를 통해 주입될 예정)
    # 이메일 서비스 제공업체에 따라 "앱 비밀번호"를 사용해야 할 수 있습니다.
    SENDER_PASSWORD = os.getenv('EMAIL_PASSWORD') 
    
    # 1. 설정 로드
    config_data = load_config(CONFIG_FILE)

    if config_data:
        # 2. 이메일 발송
        email_sent = send_email(config_data, SENDER_PASSWORD)
        
        # 3. 결과 저장
        save_result(RESULT_FILE, email_sent)