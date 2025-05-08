# app/routes/meet_list.py
import json
from flask import Blueprint, render_template, request, session, redirect, url_for
from app.utils.db import get_connection

meet_bp = Blueprint('meet', __name__)

# 미팅 리스트 삭제 함수
@meet_bp.route('/delete/<int:meeting_id>', methods=['POST'])
def delete_meeting(meeting_id):
    user_email = session.get('email')
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 회의 생성자가 삭제하는 경우
            cursor.execute("SELECT email FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cursor.fetchone()

            if meeting and meeting['email'] == user_email:
                cursor.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
                cursor.execute("DELETE FROM meeting_invites WHERE meeting_id = %s", (meeting_id,))
                cursor.execute("DELETE FROM vote_results WHERE meeting_id = %s", (meeting_id,))
            else:
                # 초대된 유저가 삭제하는 경우
                cursor.execute("""
                    DELETE FROM meeting_invites
                    WHERE meeting_id = %s AND email = %s
                """, (meeting_id, user_email))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('home'))

# 미팅 리스트 리스팅 함수(내가 만든 미팅 + 내가 초대된 미팅 모두 조회)
def show_lists():
    user_email = session.get('email')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.* FROM meetings m
                LEFT JOIN meeting_invites mi ON m.id = mi.meeting_id
                WHERE (m.email = %s OR mi.email = %s)
                AND m.created_at >= NOW() - INTERVAL 30 DAY
                GROUP BY m.id
                ORDER BY m.created_at DESC
                LIMIT %s OFFSET %s
            """, (user_email, user_email, per_page, offset))
            meetings = cursor.fetchall()

            for meeting in meetings:
                if 'selected_dates' in meeting and meeting['selected_dates']:
                    meeting['selected_dates'] = json.loads(meeting['selected_dates'])

            cursor.execute("""
                SELECT COUNT(DISTINCT m.id) AS total FROM meetings m
                LEFT JOIN meeting_invites mi ON m.id = mi.meeting_id
                WHERE (m.email = %s OR mi.email = %s)
                AND m.created_at >= NOW() - INTERVAL 30 DAY
            """, (user_email, user_email))
            total = cursor.fetchone()['total']

    finally:
        conn.close()

    return render_template('lists.html',
                           meetings=meetings,
                           current_page=page,
                           total_pages=(total + per_page - 1) // per_page)

