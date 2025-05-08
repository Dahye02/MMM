# app/routes/create_meet.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.utils.db import get_connection
from app.utils.invite_utils import send_invitation_email
import json
from datetime import datetime

create_bp = Blueprint('create', __name__)

# 미팅 생성 함수
@create_bp.route('/create', methods=['GET', 'POST'])
def create_meeting():
    if request.method == 'POST':
        title = request.form.get('title')
        deadline = request.form.get('deadline')
        selected_dates_json = request.form.get('selected_dates') or "[]"
        invited_emails_json = request.form.get('invited_emails') or "[]"

        user_email = session.get('email')
        if not user_email:
            return redirect(url_for('home'))

        try:
            selected_dates = json.loads(selected_dates_json)
            invited_emails = json.loads(invited_emails_json)
        except json.JSONDecodeError:
            selected_dates = []
            invited_emails = []

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # meetings 테이블 저장
                cursor.execute("""
                    INSERT INTO meetings (email, title, deadline, selected_dates)
                    VALUES (%s, %s, %s, %s)
                """, (user_email, title, deadline, selected_dates_json))
                meeting_id = cursor.lastrowid

                # 초대한 이메일 저장
                for email in invited_emails:
                    cursor.execute("""
                        INSERT IGNORE INTO meeting_invites (meeting_id, email)
                        VALUES (%s, %s)
                    """, (meeting_id, email))

                # invited 테이블에 저장
                for invitee in invited_emails:
                    cursor.execute("""
                        INSERT INTO invited (meeting_id, email)
                        VALUES (%s, %s)
                    """, (meeting_id, invitee))

        finally:
            conn.commit()
            conn.close()

        # 이메일 발송 (이름 조회 생략 시 이메일 그대로)
        for invitee in invited_emails:
            send_invitation_email(invitee, meeting_id)

        return redirect(url_for('home'))

    return render_template('create.html')

# 외부 접근 차단 함수
@create_bp.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email')

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            exists = result['cnt'] > 0
    finally:
        conn.close()

    return jsonify({'exists': exists})