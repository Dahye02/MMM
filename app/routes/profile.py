# app/routes/profile.py
import re
from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.utils.db import get_connection

profile_bp = Blueprint('profile', __name__)

# 사용자 프로필 함수
@profile_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('home'))

    error = None
    success = None

    # 사용자 정보 가져오기
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT email, name, phone, password, agreed_notify
                FROM users WHERE email = %s
            """, (user_email,))
            user = cursor.fetchone()
    finally:
        conn.close()

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        agreed_notify = request.form.get('agreed_notify') == 'on'

        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')

        # 유효성 검증
        if agreed_notify and not phone:
            error = "전화번호를 입력해주세요."
        elif phone and not re.match(r'^010\d{8}$', phone):
            error = "전화번호 형식을 확인해주세요. 예: 01012345678"
        elif not current_pw:
            error = "현재 비밀번호를 입력해주세요."
        elif not check_password_hash(user['password'], current_pw):
            error = "현재 비밀번호가 일치하지 않습니다."
        elif new_pw and new_pw != confirm_pw:
            error = "새 비밀번호가 일치하지 않습니다."

        if error:
            return render_template("profile.html", user=user, error=error)

        # 업데이트
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET name = %s, phone = %s, agreed_notify = %s
                    WHERE email = %s
                """, (name, phone, int(agreed_notify), user_email))

                if new_pw:
                    hashed_pw = generate_password_hash(new_pw)
                    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_pw, user_email))

            conn.commit()

            # 최신 정보 재조회
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT email, name, phone, password, agreed_notify
                    FROM users WHERE email = %s
                """, (user_email,))
                user = cursor.fetchone()

            success = "정보가 성공적으로 수정되었습니다."
        finally:
            conn.close()

    return render_template("profile.html", user=user, error=error, success=success)