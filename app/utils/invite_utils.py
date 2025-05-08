# app/utils/invite_utils.py
from flask import current_app, url_for
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_invitation_email(email, meeting_id):
    vote_link = url_for('vote.vote_meeting', meeting_id=meeting_id, _external=True)
    subject = "📨 회의 일정 투표에 초대합니다"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px;">
          <h2 style="color: #2c3e50;">👋 안녕하세요!</h2>
          <p style="font-size: 16px; color: #333;">
            <strong>회의 일정 투표</strong>에 초대되었습니다.<br><br>
            아래 버튼을 클릭하여 투표에 참여해 주세요.
          </p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{vote_link}" style="background-color: #3498db; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-size: 16px;">
              ✏️ 지금 투표하기
            </a>
          </div>
          <p style="font-size: 14px; color: #888;">감사합니다.<br>회의 일정 조율 시스템 드림</p>
        </div>
      </body>
    </html>
    """

    msg = Message(subject=subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email],
                  html=html_body)
    mail.send(msg)
