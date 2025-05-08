# app.py
import subprocess
import pkg_resources
import os

# 패키지 설치 함수
def install_requirements():
    with open('requirements.txt') as f:
        required = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    installed = {pkg.key for pkg in pkg_resources.working_set}
    to_install = [pkg for pkg in required if pkg.split('==')[0].lower() not in installed]

    if to_install:
        print("📦 누락된 패키지 설치 중:", to_install)
        subprocess.check_call(['pip', 'install'] + to_install)
    else:
        print("✅ 모든 패키지가 이미 설치되어 있습니다.")

from app import create_app

install_requirements()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
