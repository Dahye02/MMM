<<<<<<< HEAD
# MMM
=======
# 📅 MeetVote - 일정 투표 플랫폼

**MeetVote**는 회의 일정을 손쉽게 조율할 수 있는 웹 기반 투표 플랫폼입니다.  
Google 이메일 로그인, 일정 선택, 초대, 투표 결과 시각화까지 모두 지원합니다.

---

## 🚀 주요 기능

- 이메일 기반 회원가입 및 로그인
- 회의 생성 (일정 후보 및 마감일 지정)
- 사용자 초대 및 재초대 메일 전송
- 달력 UI를 통한 일정 투표 기능
- 각 날짜에 투표한 인원 수 및 이름 표시
- 생성자와 초대자 권한 분리 (삭제 / 나가기)
- '내가 생성' / '초대됨' 태그로 회의 구분

---

## ⚙️ 기술 스택

- **Backend**: Python, Flask, Flask-Mail
- **Frontend**: HTML, CSS, JavaScript, FullCalendar.js
- **Database**: MySQL (pymysql)
- **Infra**: AWS Cloud9

---

## 📁 디렉토리 구조
app/
├── routes/ # 라우터 모듈
├── templates/ # Jinja2 HTML 템플릿
├── static/ # CSS/JS 정적 파일
├── utils/ # 이메일 전송 등 유틸
├── db.py # DB 연결
└── init.py # Flask 앱 초기화
index.py # 앱 실행 엔트리

---

## 📦 설치 및 실행 방법

```bash
# 1. 프로젝트 클론
git clone https://github.com/yourname/meetvote.git
cd meetvote

# 2. 가상환경 설정
python3 -m venv venv
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경 변수 설정 (.env 또는 직접 설정)
#    - FLASK_SECRET_KEY
#    - MAIL_USERNAME / MAIL_PASSWORD

# 5. 실행

---

## 👩‍💻 개발자

**정다혜 (Jung Dahye)**  
정보보안 전공 기반의 웹 보안 및 사용자 경험에 관심 있는 개발자입니다.  
보안성과 사용성을 모두 잡는 웹 애플리케이션을 지향하며,  
실제 사용자 입장에서 가장 간편한 UI/UX를 고민합니다.

- ✉️ Email: jts9006@naver.com
- 🏫 Major: Information Security
- 🌱 Interest: Cybersecurity · Web Dev Engineering
>>>>>>> eedc8e4 (MMM Project)
