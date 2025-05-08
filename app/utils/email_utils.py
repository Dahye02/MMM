# app/utils/email_utils.py
import random, string
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for, Blueprint
from werkzeug.security import generate_password_hash

from app.utils.db import get_connection

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def get_serializer():
    return URLSafeTimedSerializer(current_app.secret_key)

def generate_temp_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

def send_verification_email(email):
    serializer = get_serializer()
    token = serializer.dumps(email, salt='email-confirm')
    verify_url = url_for('verify.verify_email', token=token, _external=True)

    subject = "📩 이메일 인증을 완료해 주세요"
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f2f2f2; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50;">이메일 인증 요청</h2>
          <p style="font-size: 16px; color: #333;">
            아래 버튼을 클릭하여 이메일 인증을 완료해 주세요.
          </p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_url}" style="background-color: #27ae60; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none;">
              🔒 이메일 인증하기
            </a>
          </div>
          <p style="font-size: 14px; color: #888;">이 링크는 1시간 동안만 유효합니다.</p>
          <p style="font-size: 14px; color: #888;">감사합니다.<br>서비스팀 드림</p>
        </div>
      </body>
    </html>
    """

    msg = Message('이메일 인증',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email],
                  html=html_body)
    mail.send(msg)

def send_temp_password_email(email, temp_password):
    subject = "🔐 임시 비밀번호 안내"
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f2f2f2; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50;">임시 비밀번호가 발급되었습니다</h2>
          <p style="font-size: 16px; color: #333;">
            아래의 임시 비밀번호로 로그인해 주세요:
          </p>
          <div style="text-align: center; margin: 20px 0;">
            <p style="font-size: 20px; font-weight: bold; background-color: #f0f0f0; padding: 10px 20px; border-radius: 6px; display: inline-block;">{temp_password}</p>
          </div>
          <p style="font-size: 14px; color: #555;">로그인 후 반드시 마이페이지에서 비밀번호를 변경해 주세요.</p>
          <p style="font-size: 14px; color: #888;">감사합니다.<br>서비스팀 드림</p>
        </div>
      </body>
    </html>
    """

    msg = Message('임시 비밀번호 안내',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email],
                  html=html_body)
    mail.send(msg)

def send_reset_request_email(email):
    serializer = get_serializer()
    token = serializer.dumps(email, salt='password-reset-request')
    reset_url = url_for('verify.confirm_reset', token=token, _external=True)

    subject = "🔁 비밀번호 초기화 요청"
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f2f2f2; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          <h2 style="color: #2c3e50;">비밀번호 초기화 요청</h2>
          <p style="font-size: 16px; color: #333;">
            비밀번호 재설정을 요청하셨다면, 아래 버튼을 눌러주세요.
          </p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #e67e22; color: white; padding: 12px 24px; border-radius: 5px; text-decoration: none;">
              🔄 비밀번호 재설정
            </a>
          </div>
          <p style="font-size: 14px; color: #555;">
            이 링크는 <strong>30분간</strong> 유효합니다.<br>
            요청하지 않으셨다면 이 메일을 무시하셔도 됩니다.
          </p>
          <p style="font-size: 14px; color: #888;">감사합니다.<br>서비스팀 드림</p>
        </div>
      </body>
    </html>
    """

    msg = Message('비밀번호 초기화 요청',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email],
                  html=html_body)
    mail.send(msg)

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verify/<token>')
def verify_email(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET is_verified = 1 WHERE email = %s", (email,))
        conn.commit()
        return "✅ 이메일 인증 완료!"
    except Exception as e:
        print(f"[ERROR] 이메일 인증 실패: {e}")
        return "❌ 인증 링크가 유효하지 않거나 만료되었습니다."

@verify_bp.route('/confirm-reset/<token>')
def confirm_reset(token):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt='password-reset-request', max_age=1800)
        temp_password = generate_temp_password()
        hashed = generate_password_hash(temp_password)

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed, email))
        conn.commit()

        send_temp_password_email(email, temp_password)
        return "✅ 임시 비밀번호를 이메일로 전송했습니다. 로그인 후 꼭 변경해주세요."
    except Exception as e:
        print(f"[ERROR] 임시 비밀번호 발급 실패: {e}")
        return "❌ 유효하지 않거나 만료된 링크입니다. 다시 시도해주세요."
