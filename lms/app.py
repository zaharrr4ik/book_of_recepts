from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import random

# Инициализация Flask приложения и конфигурация
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'  # Секретный ключ для сессий и защиты форм
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Путь к SQLite базе
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Папка для загрузки файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(100))
    dishes = db.relationship('Dish', backref='author')


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    photo = db.Column(db.String(100))
    ingredients = db.Column(db.Text)
    recipe_steps = db.Column(db.Text)
    calories = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Загружает пользователя по ID для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Проверяет разрешенные расширения файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Перенаправляет с главной на страницу входа
@app.route('/')
def home():
    return redirect(url_for('login'))


# Обрабатывает вход пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль')
    return render_template('login.html')


# Регистрирует нового пользователя
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        existing_user = User.query.filter_by(username=request.form['username']).first()
        if existing_user:
            flash('Этот логин уже занят')
            return redirect(url_for('register'))
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')


# Главная страница с блюдами
@app.route('/index')
@login_required
def index():
    dishes = Dish.query.all()
    gallery_images = [f'dish{i}.jpg' for i in random.sample(range(1, 13), 3)]
    return render_template('index.html', dishes=dishes, gallery_images=gallery_images)


# Показывает профиль пользователя
@app.route('/profile/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    dishes = Dish.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, dishes=dishes)


# Добавляет новое блюдо
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_dish():
    if request.method == 'POST':
        if 'photo' not in request.files:
            flash('Не выбрано фото блюда')
            return redirect(request.url)
        file = request.files['photo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            dish = Dish(
                name=request.form['name'],
                photo=filename,
                ingredients=request.form['ingredients'],
                recipe_steps=request.form['recipe_steps'],
                calories=int(request.form.get('calories', 0)),
                user_id=current_user.id
            )
            db.session.add(dish)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('add_dish.html')


# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Показывает детали блюда
@app.route('/dish/<int:dish_id>')
@login_required
def view_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    return render_template('dish_detail.html', dish=dish)


# Удаляет блюдо
@app.route('/delete_dish/<int:dish_id>', methods=['POST'])
@login_required
def delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    if dish.photo:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], dish.photo))
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
    db.session.delete(dish)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        db.create_all()
    app.run(debug=True)
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
