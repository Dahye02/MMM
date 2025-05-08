# 📅 일정 투표 플랫폼 MMM

**MeetVote**는 회의 일정을 손쉽게 조율할 수 있는 웹 기반 투표 플랫폼입니다.  
Google 이메일 로그인, 일정 선택, 초대, 투표 결과 시각화까지 모두 지원합니다.


<br><br><br>
## 🚀 주요 기능

- 이메일 기반 회원가입 및 로그인
- 회의 생성 및 삭제 (일정 후보 및 마감일 지정)
- 사용자 초대 메일 전송
- 달력 UI를 통한 일정 투표 기능
- 각 날짜에 투표한 인원 수 및 이름 표시
<br><br>


## ⚙️ 기술 스택

- **Backend**: Python, Flask, Flask-Mail
- **Frontend**: HTML, CSS, JavaScript, FullCalendar.js
- **Database**: MySQL (pymysql)
- **Infra**: AWS Cloud9
<br><br>


## 📁 디렉토리 구조
app/<br>
├── routes/<br>
├── templates/<br>
├── static/<br>
├── utils/<br>
├── db.py<br>
└── init.py<br>
index.py<br><br>



## 📦 설치 및 실행 방법

```bash
# 1. 프로젝트 클론
git clone https://github.com/yourname/meetvote.git
cd meetvote

# 2. 가상환경 설정
python3 -m venv venv
source venv/bin/activate

# 3. 환경 변수 설정 (.env 또는 직접 설정)
    - FLASK_SECRET_KEY
    - MAIL_USERNAME / MAIL_PASSWORD

# 4. 실행
```


## 👩‍💻 개발자

**정다혜 (Jeong Dahye)**  
- ✉️ Email: jts9006@naver.com
- 🏫 Major: Information Security
- 🌱 Interest: Cybersecurity · Web Dev Engineering
