from flask import Flask, render_template, redirect, request, url_for, flash
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
import werkzeug
from flask_login import LoginManager, login_user, current_user, UserMixin, logout_user, login_required
from dotenv import load_dotenv
import requests
from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
Bootstrap5(app)

class LoginForm(FlaskForm):
    email = EmailField('', validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password = PasswordField('', render_kw={'placeholder': 'Password'}, validators=[DataRequired()])
    submit = SubmitField("Login")

class RecipeSearch:
    
    
    def __init__(self):
        load_dotenv()
        self.RECIPE_ID = os.environ.get("recipe_id")
        self.RECIPE_KEY = os.environ.get("recipe_key")
        self.PARAMS = {
            "type": "public",
            "app_id": self.RECIPE_ID,
            "app_key": self.RECIPE_KEY,
            "random": True
        }


    def query(self, input):
        self.PARAMS["q"] = input

    
    def diet(self, diet_input):
        self.PARAMS["diet"] = diet_input

    
    def health(self, health_input):
        self.PARAMS["health"] = health_input


    def cuisine_type(self, cuisine_input):
        self.PARAMS["cuisineType"] = cuisine_input
    

    def meal_type(self, meal_input):
        self.PARAMS["mealType"] = meal_input

    
    def is_random(self):
        return self.PARAMS["random"]
    

    def change_random(self, boolean):
        self.PARAMS["random"] = boolean


    def search(self):
        self.response = requests.get("https://api.edamam.com/api/recipes/v2", params=self.PARAMS)
        self.response.raise_for_status()
        self.data = self.response.json()
        return self.data
    
    def results(self):
        return self.data
recipe_search = RecipeSearch()

# setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)


class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(250), unique=False, nullable=False)
    name = db.Column(db.String(250), unique=True, nullable=False)
    image = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    DIET_OPTIONS = [
    "balanced",
    "high-fiber",
    "high-protein",
    "low-carb",
    "low-fat",
    "low-sodium"
]

    HEALTH_OPTIONS = [
    "alcohol-free",
    "celery-free",
    "crustacean-free",
    "dairy-free",
    "DASH",
    "egg-free",
    "fish-free",
    "gluten-free",
    "immuno-supportive",
    "keto-friendly",
    "kidney-friendly",
    "kosher",
    "low-potassium",
    "low-sugar",
    "Mediterranean",
    "mustard-free",
    "no-oil-added",
    "paleo",
    "peanut-free",
    "pescatarian",
    "pork-free",
    "red-meat-free",
    "sesame-free",
    "shellfish-free",
    "soy-free",
    "tree-nut-free",
    "vegan",
    "vegetarian",
    "wheat-free"
]

    CUISINE_OPTIONS = [
    "American",
    "Asian",
    "British",
    "Caribbean",
    "Central Europe",
    "Chinese",
    "Eastern Europe",
    "French",
    "Indian",
    "Italian",
    "Japanese",
    "Mexican",
    "Middle Eastern",
    "Nordic",
    "South American",
    "South East Asian"
]

    MEAL_OPTIONS = [
    "Breakfast",
    "Lunch",
    "Dinner",
    "Snack"
]
    print(len(DIET_OPTIONS) + len(HEALTH_OPTIONS) + len(CUISINE_OPTIONS) + len(MEAL_OPTIONS))
    return render_template('index.html', diet=DIET_OPTIONS, health=HEALTH_OPTIONS, cuisine=CUISINE_OPTIONS, meal=MEAL_OPTIONS, current_user=current_user)


@app.route('/search', methods=["GET", "POST"])
def search():
    ingredients = request.args['ingredients']
    recipe_search.query(ingredients)

    try:
        diet = request.args['diet']
        recipe_search.diet(diet)
    except:
        pass

    try:
        diet = request.args['health']
        recipe_search.health(diet)
    except:
        pass

    try:
        diet = request.args['cuisine']
        recipe_search.cuisine_type(diet)
    except:
        pass

    try:
        diet = request.args['meal']
        recipe_search.meal_type(diet)
    except:
        pass
    recipe_search.search()
    return redirect(url_for('results'))


@app.route('/results')
def results():
    global results
    results = recipe_search.results()
    return render_template('results.html', results=results, current_user=current_user)


@app.route('/about')
def about():
    return render_template('about.html', current_user=current_user)

# saving recipes
@app.route('/myrecipes')
@login_required
def my_recipes():
    name_results = db.session.execute(db.select(Recipe.name).where(Recipe.user_id == userid))
    img_results = db.session.execute(db.select(Recipe.image).where(Recipe.user_id == userid))
    link_results = db.session.execute(db.select(Recipe.link).where(Recipe.user_id == userid))
    names = name_results.scalars().all()
    images = img_results.scalars().all()
    links = link_results.scalars().all()
    return render_template('my_recipes.html', names=names, images=images, links=links)

@app.route('/results/<index>')
@login_required
def save(index):
    saved_recipe = Recipe(
        name = results['hits'][int(index)]['recipe']['label'],
        user_id = userid,
        image = results['hits'][int(index)]['recipe']['image'],
        link = results['hits'][int(index)]['recipe']['url']
    )
    db.session.add(saved_recipe)
    db.session.commit()
    return redirect(url_for('results'))

# register user
@app.route('/register', methods=["GET", "POST"])
def register_page():
    return render_template('register.html', current_user=current_user)

@app.route('/register/complete', methods=["GET", "POST"])
def register_complete():
    result = db.session.execute(db.select(User).where(User.email == request.args['email']))
    user = result.scalar()
    if user:
        flash("Email already registered, please sign in.")
        return redirect(url_for('login'))
       
    hash_pass = werkzeug.security.generate_password_hash(password=request.args['password'], method='pbkdf2:sha256', salt_length=8)
    new_user = User(
        email = request.args['email'],
        password = hash_pass
    )
    db.session.add(new_user)
    db.session.commit()
    next = request.args.get('next')
    global userid
    userid = request.args['email']
    login_user(new_user)
    return redirect(next or url_for('home'))


# login user
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if user and werkzeug.security.check_password_hash(user.password, password):
            next = request.args.get('next')
            global userid
            userid = email
            login_user(user)
            return redirect(next or url_for('home'))
        elif not user:
            flash('This email does not exist, please try again.')

        elif not werkzeug.security.check_password_hash(user.password, password):
            flash('Incorrect Password, please try again.')
 
    return render_template('login.html', form=form, current_user=current_user)

# logout user
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    next = request.args.get('next')
    logout_user()
    return redirect(next or url_for('home'))


with app.app_context():
    db.create_all()
