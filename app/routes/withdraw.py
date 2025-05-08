# app/routes/withdraw.py
from flask import Blueprint, render_template, session, redirect, url_for, request

from app.utils.db import get_connection

withdraw_bp = Blueprint('withdraw', __name__)

# 회원탈퇴 함수
@withdraw_bp.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('home'))

    if request.method == 'POST':
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE email = %s", (user_email,))
            conn.commit()
        finally:
            conn.close()

        session.clear()
        return redirect(url_for('home'))

    return render_template('withdraw.html')
