# app/routes/vote.py
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.utils.db import get_connection
from app.utils.invite_utils import send_invitation_email
import json

vote_bp = Blueprint('vote', __name__)

# 투표 기능 함수
@vote_bp.route('/vote/<int:meeting_id>', methods=['GET'])
def vote_meeting(meeting_id):
    user_email = session.get('email')
    if not user_email:
        return redirect(url_for('home'))

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 회의 정보 조회
            cursor.execute("SELECT * FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cursor.fetchone()
            if not meeting:
                return "회의가 존재하지 않습니다.", 404

            selected_dates = json.loads(meeting['selected_dates'])

            # 본인 투표 내역
            cursor.execute("""
                SELECT selected_dates FROM vote_results
                WHERE meeting_id = %s AND email = %s
            """, (meeting_id, user_email))
            previous_vote = cursor.fetchone()
            previous_dates = json.loads(previous_vote['selected_dates']) if previous_vote else []

            # 초대된 사용자 목록 및 투표 여부
            cursor.execute("""
                SELECT u.name, mi.email,
                CASE WHEN vr.email IS NOT NULL THEN 1 ELSE 0 END AS voted
                FROM meeting_invites mi
                LEFT JOIN users u ON u.email = mi.email
                LEFT JOIN vote_results vr ON vr.email = mi.email AND vr.meeting_id = mi.meeting_id
                WHERE mi.meeting_id = %s
            """, (meeting_id,))
            invited_info = cursor.fetchall()

            # 전체 투표 정보
            cursor.execute("""
                SELECT u.name, v.selected_dates FROM vote_results v
                JOIN users u ON u.email = v.email
                WHERE v.meeting_id = %s
            """, (meeting_id,))
            rows = cursor.fetchall()

            votes_by_date = {date: [] for date in selected_dates}
            for row in rows:
                dates = json.loads(row['selected_dates'])
                for d in dates:
                    if d in votes_by_date:
                        votes_by_date[d].append(row['name'])

    finally:
        conn.close()

    is_creator = meeting['email'] == user_email

    return render_template("vote.html",
                           meeting=meeting,
                           my_votes=previous_dates,
                           votes_by_date=votes_by_date,
                           invited_info=invited_info,
                           is_creator=is_creator)


# 투표 조회 함수
@vote_bp.route('/submit_vote/<int:meeting_id>', methods=['POST'])
def submit_vote(meeting_id):
    user_email = session.get('email')
    selected_dates = request.json.get('selected_dates', [])

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 투표 삽입 또는 수정
            cursor.execute("""
                INSERT INTO vote_results (meeting_id, email, selected_dates)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE selected_dates = VALUES(selected_dates)
            """, (meeting_id, user_email, json.dumps(selected_dates)))
            conn.commit()

            # 최신 투표 정보 다시 조회
            cursor.execute("""
                SELECT u.name, v.selected_dates FROM vote_results v
                JOIN users u ON v.email = u.email
                WHERE v.meeting_id = %s
            """, (meeting_id,))
            rows = cursor.fetchall()

            updated_votes = {}
            for row in rows:
                dates = json.loads(row['selected_dates'])
                for d in dates:
                    if d not in updated_votes:
                        updated_votes[d] = []
                    updated_votes[d].append(row['name'])
    finally:
        conn.close()

    return jsonify({
        'status': 'ok',
        'votes_by_date': updated_votes
    })

# 투표 재전송 함수
@vote_bp.route('/resend_invites/<int:meeting_id>', methods=['POST'])
def resend_invites(meeting_id):
    data = request.get_json()
    emails = data.get('emails', [])

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for email in emails:
                # 초대 테이블에 추가 (중복 방지)
                cursor.execute("""
                    INSERT IGNORE INTO meeting_invites (meeting_id, email)
                    VALUES (%s, %s)
                """, (meeting_id, email))

                # 메일 발송
                send_invitation_email(email, meeting_id)
        conn.commit()
    finally:
        conn.close()

    return jsonify({'status': 'sent'})
