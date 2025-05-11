class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    photo = db.Column(db.String(100))  # Путь к изображению
    ingredients = db.Column(db.Text)
    recipe_steps = db.Column(db.Text)  # Рецепт по пунктам
    calories = db.Column(db.Integer)   # Количество калорий
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))