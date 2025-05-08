# app/routes/legal.py
from flask import Blueprint, render_template

legal_bp = Blueprint('legal', __name__)

# 개인정보처리방침
@legal_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

# 이용약관
@legal_bp.route('/terms')
def terms():
    return render_template('terms.html')
