# app/routes/login.py
import re
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from app.utils.db import get_connection
from app.utils.email_utils import send_reset_request_email, send_temp_password_email, generate_temp_password, send_verification_email

login_bp = Blueprint('login', __name__)

# 회원가입 함수
@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        agreed_notify = 1 if request.form.get('agreed_notify') == '1' else 0

        if not (name and email and password):
            return render_template('register.html', error="모든 필수 항목을 입력해주세요.")

        # 이메일 검사
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            return render_template('register.html', error="올바른 이메일 형식을 입력해주세요.")

        # 비밀번호 검사
        if len(password) < 6:
            return render_template('register.html', error="비밀번호는 최소 6자 이상이어야 합니다.")

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 중복가입 방지
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return render_template('register.html', error="이미 가입한 이메일입니다.")

                # 사용자 추가
                sql = """
                    INSERT INTO users (email, name, password, phone, agreed_notify, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (email, name, hashed_password, phone, agreed_notify, False))
            conn.commit()

            send_verification_email(email)

            return render_template('login.html', success_message="회원가입 완료! 이메일 인증을 진행해주세요.")
        finally:
            conn.close()

    return render_template('register.html')

# 로그인 함수
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if not user:
                    return render_template('login.html', error="가입된 이메일이 없습니다. 회원가입을 진행해주세요.")

                if not check_password_hash(user['password'], password):
                    return render_template('login.html', error="비밀번호가 틀렸습니다.")

                if not user.get('is_verified'):
                    return render_template('login.html', error="이메일 인증이 완료되지 않았습니다. 메일함을 확인해주세요.")

                # 로그인 성공
                session.permanent = True
                session['logged_in'] = True
                session['email'] = email
                return redirect(url_for('home'))
        finally:
            conn.close()

    return render_template('login.html')

# 비밀번호 찾기 함수(임시 비밀번호 요청)
@login_bp.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if not user:
                    return render_template('forgot.html', error="가입된 이메일이 없습니다.")

                # 임시 비밀번호 발급
                send_reset_request_email(email)

                return render_template('login.html', success_message="임시 비밀번호 발급 메일을 전송했습니다.")
        finally:
            conn.close()

    return render_template('forgot.html')

# 로그아웃 함수
@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))