# Просто импортируем app из основного файла
from app import app

# Для совместимости с Glitch
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)