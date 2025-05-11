import os
import json
from app import app

def setup_glitch():
    """Автоматическая настройка для Glitch"""
    if not os.path.exists('server.py'):
        with open('server.py', 'w') as f:
            f.write("""from app import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
""")

    # 2. Создаем start.sh
    start_sh_content = """#!/bin/bash
set -eu
export PYTHONUNBUFFERED=true
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python server.py
"""
    with open('start.sh', 'w') as f:
        f.write(start_sh_content)
    os.chmod('start.sh', 0o755)

    # 3. Создаем .env с настройками
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(f"SECRET_KEY={app.config['SECRET_KEY']}\n")
            f.write(f"DATABASE_URL=sqlite:///site.db\n")

    print("Glitch setup complete!")

if __name__ == '__main__':
    setup_glitch()