# PYTHON MODULES
import os, ast
from datetime import date, timedelta

# FLASK MODULES
from flask import Flask, redirect, render_template, request, flash, session, g, abort, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError   # for already taken usernames

# SPECIAL MODULES
from fatsecret import Fatsecret

# MY MODULES
from forms import UserAddForm, LoginForm
from models import db, connect_db, Food, FoodServing, FoodLog, User

# SENSITIVE DATA MANAGEMENT
try:
    # IF THERE IS A HIDDEN FILE (LOCAL)
    from hidden import CONSUMER_KEY, CONSUMER_SECRET
except:
    # IF THERE IS NO HIDDEN FILE (HEROKU)
    CONSUMER_KEY = None
    CONSUMER_SECRET = None

# CREATE SESSION KEYS
CURR_USER_KEY = "curr_user"
DATE_KEY = "the_date"
FOOD_KEY = "food"

app = Flask(__name__)

# DATABASE CONNECTION
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get(
        "DATABASE_URL",    # IF THERE IS AN ENV_VAR
        "postgresql:///calorie_db"   # LOCAL VAR
    )
)

# HEROKU POSTGRESQL ADDRESS FIX
app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgres://", "postgresql://", 1)

# OTHER CONFIGURATIONS
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False   # SWITCHED
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", API_SECRET_KEY)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "top_secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

CONSUMER_KEY = os.environ.get(
    "CONSUMER_KEY",   # REMOTE
    CONSUMER_KEY      # LOCAL
)

CONSUMER_SECRET = os.environ.get(
    "CONSUMER_SECRET",   # REMOTE
    CONSUMER_SECRET      # LOCAL
)

fs = Fatsecret(CONSUMER_KEY, CONSUMER_SECRET)
# BASE_URL = "https://platform.fatsecret.com/rest/server.api"

# db.drop_all()
# db.create_all()


##################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr_user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None
    

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def load_the_date():
    """Load the date."""

    return date.fromisoformat(session[DATE_KEY])


def save_(the_date):
    """Save the date."""

    session[DATE_KEY] = the_date.isoformat()


def logged_in():
    # print("#"*30)
    # print(">"*5, "   LOGIN CHECK:")
    if session.get(CURR_USER_KEY):
        if g.user and g.user.id == session[CURR_USER_KEY]:
            # if g.user.id == session[CURR_USER_KEY]:
                # print(">"*5, "   USER IS LOGGED IN!")
                # print("#"*30)
            return True
        else:
            del session[CURR_USER_KEY]
    # print(">"*5, "   NO LOGGED IN USER!")
    # print("#"*30)
    return False


def print_(date):
    """Print todays date on terminal"""
    
    print("#"*30)
    print(f"'/home' date => {date} - {type(date)}")
    print("#"*30)


def yaz(item):
    """Print the item on terminal"""
    
    print("#"*30)
    # print(f"'/home' TODAY => {date} - {type(date)}")
    print(">"*5, "    ", item)
    print("#"*30)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If  there already is a user with that username: flash message and re-present the form.
    """

    do_logout()

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                calorie_need=form.calorie_need.data,
                calorie_limit=form.calorie_limit.data
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)
        
        do_login(user)

        return redirect('/')
    
    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", 'success')
            return redirect('/')

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


##################################################################
# ROUTES

@app.route('/home')
def homepage():
    """We start here!"""

    if not logged_in():
        return redirect('/')
    
    TODAY = date.today()
    # print_(TODAY)

    # FIND OUT THE DATE
    THE_DATE = load_the_date()
    # print_(THE_DATE)

    # USER'S FOODLOG FOR THE DAY (flud)
    flud = FoodLog.query.filter(FoodLog.user_id == g.user.id,
                                FoodLog.date == THE_DATE)
    calorie_list = []
    if flud.count() > 0:
        for df in flud.all():
            df.calories = round(df.calories)
        calorie_list = [df.calories for df in flud.all()]

    return render_template(
        'home.html', 
        user=g.user, 
        today=TODAY, 
        the_date=THE_DATE, 
        foodlog=flud.all(),
        calorie_sum=sum(calorie_list)
    )


@app.route('/food/search', methods=["POST"])
def search_food():

    if not logged_in():
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    food = request.form["food"]
    
    try:
        food_list = fs.foods_search(food)
        return redirect(f"/food/search/{food}/{0}")

    except:
        return render_template(
            '/errors/search.html', 
            user=g.user, 
            today=TODAY, 
            the_date=THE_DATE, 
            search_term=food
        )


@app.route('/food/search/<food>/<int:page_num>')
def search_food_redirect(food, page_num):
    """ Make the Fatsecret API search and return the results
    """

    if not logged_in():
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    max_results = 20
    last_page = False

    # SEARCH RESULTS FROM FATSECRET API
    # ---------------------------------
    # ['brand_name': 'Great Value',  ==>>  //   NO BRAND NAME WHEN food_type IS 'Generic'
    #  'food_description': 'Per 3 pieces - Calories: 130kcal | Fat: 0.00g | Carbs: 33.00g | Protein: 0.00g',
    #  'food_id': '3305099',
    #  'food_name': 'Orange Slices',
    #  'food_type': 'Brand',
    #  'food_url': 'https://www.fatsecret.com/calories-nutrition/great-value/orange-slices'},
    #  { ... }, ... ]
    
    food_list = fs.foods_search(food,
                                page_number=page_num,
                                max_results=max_results)

    try:
        fs.foods_search(food,
                        page_number=page_num+1,
                        max_results=max_results)

    except:
        last_page = True

    try:
        # MANY RESULTS
        food_list[0].get('food_id')

    except:
        # ONLY ONE RESULT
        food_list=[food_list]
    
    return render_template(
        '/foods/search.html', 
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE,
        food_list=food_list, 
        search_term=food,
        page_number=page_num,
        last_page=last_page
    )


@app.route('/food/add/<int:food_id>', methods=["GET", "POST"])
def add_food(food_id):
    """takes the chosen food and calculates its values
    """

    if not logged_in():
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    # POST
    if request.form:

        amount = float(request.form["amount"])
        servings_str = request.form["servings"]

        # string to tuple conversion
        food_id, serving_id = ast.literal_eval(servings_str.strip())

        food_id = int(food_id)

        foodinfo = session[FOOD_KEY] 
        serv = foodinfo['servings']['serving']

        # DATABASE REGISTERING OF FOOD & ITS INFO
        try:
            Food.query.filter_by(id=food_id).one()
            # yaz("THE FOOD IS PRESENT IN DB !!")
        except:
            # yaz("THE FOOD NEEDS TO BE SAVED IN DB !!")
            brand = foodinfo.get('brand_name') or "Generic"

            food = Food(
                id=food_id,
                name=foodinfo['food_name'],
                brand=brand,
                food_url=foodinfo['food_url']
            )

            db.session.add(food)
            db.session.commit()

            # SEND FOOD INFO TO LOCAL DATABASE
            try:
                # ONE SERVING
                serv.get('fat')
                food_info = FoodServing(food_id=food_id, **serv)
                db.session.add(food_info)

            except:
                # LIST SERVING
                for s in serv:
                    food_info = FoodServing(food_id=food_id, **s)
                    db.session.add(food_info)

            db.session.commit()

        # SEND FOOD-LOG TO DATABASE
        try:
            serving_info = FoodServing.query.filter_by(serving_id=serving_id).one()

        except:       
            return render_template(
                        '/errors/database.html', 
                        user=g.user, 
                        today=TODAY,
                        the_date=THE_DATE, 
                    )
        
        print("food_id")
        print(food_id)
        print("serving_id")
        print(serving_id)
        print("serv")
        print(serv)

        # make serv a list if it is only one item
        try:
            serv[0]
        except:
            serv = [serv]

        number_of_units = [float(s['number_of_units']) for s in serv if s['serving_id'] == str(serving_id)][0]

        calories = serving_info.calories * amount / number_of_units
        
        foodlog = FoodLog(
            user_id=g.user.id,
            food_id=food_id,
            serving_id=serving_info.serving_id,
            serving_description=serving_info.serving_description,
            unit_calories=serving_info.calories,
            amount=amount, 
            number_of_units=number_of_units,
            calories=calories,
            date=THE_DATE,
        )

        db.session.add(foodlog)
        db.session.commit()

        return redirect('/home')
    
    # GET REQUEST PART ###
    # --------------------
    food_info = fs.food_get(food_id)

    # save food_info in session for global access
    session[FOOD_KEY] = food_info

    serving_values = food_info['servings']['serving']
    
    # make serving_values a list if it is only one item
    try:
        serving_values[0]
    except:
        serving_values = [serving_values]
    
    # give priority to 'gram measurement'
    cals = False
    for val in serving_values:
        if val['serving_description'] == '100 g':
            cals = val['calories']
        val['metric_serving_amount'] = str(int(round(float(val['metric_serving_amount']))))

    return render_template(
        '/foods/add.html', 
        user=g.user, 
        today=TODAY, 
        the_date=THE_DATE,
        serving_values=serving_values,
        food_info=food_info,
        cals=cals
    )


@app.route('/food/edit/<int:log_id>', methods=["GET", "POST"])
def edit_food(log_id):
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not logged_in():
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()
    
    # POST METHOD
    if request.form:
        amount = float(request.form["amount"])

        log = FoodLog.query.get_or_404(log_id)
        log.amount = amount
        log.calories = log.amount * log.unit_calories / log.number_of_units

        # if log.serving_description == '100 g':
        #     log.calories /= 100

        db.session.commit()

        return redirect('/home')

    # GET REQUEST PART ###
    # --------------------
    log = FoodLog.query.get_or_404(log_id)

    return render_template(
                '/foods/edit.html',
                user=g.user, 
                the_date=THE_DATE,
                today=TODAY,
                log=log
            )


@app.route('/food/delete/<int:log_id>', methods=["POST"])
def delete_food(log_id):
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # NO NEED TO FIND OUT THE DATE

    log = FoodLog.query.get_or_404(log_id)
    
    db.session.delete(log)
    db.session.commit()

    return redirect('/home')


@app.route('/food/frequent')
def frequent_foods():
    """It lists user's most frequent eaten 20 foods by frequency
    """

    # CHECK IF THE USER LOGGED IN
    if not logged_in():
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    freq_20_foods = (
        db.session.query(
            Food, db.func.count(FoodLog.food_id))
                         .join(FoodLog)
                         .filter_by(user_id=g.user.id)
                         .group_by(Food.id)
                         .order_by(db.func.count(FoodLog.food_id)
                                          .desc())
                         .limit(20)
                         .all()
    )

    return render_template(
        '/foods/frequent.html',
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE,
        freq_20_foods=freq_20_foods,
    )


@app.route('/calendar', methods=["GET", "POST"])
def change_date():
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    if request.form:

        the_date = request.form["chosen_date"]   # STRING
        # print_(the_date)
        THE_DATE = date.fromisoformat(the_date)  # OBJECT
        save_(THE_DATE)

        return redirect('/home')

    return render_template(
        'calendar.html', 
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE,
    )


@app.route('/day-change/<direction>/<int:days>')
def change_day(direction, days):
    """Change the date."""

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    
    # print_(TODAY)   # prints to terminal

    THE_DATE = load_the_date()
    
    # print_(THE_DATE)   # prints to terminal

    t1 = timedelta(days)
    if direction == 'post':
        THE_DATE += t1
    elif direction == 'pre':
        THE_DATE -= t1
    else:
        return render_template(
            '/errors/date.html',
            user=g.user, 
            today=TODAY,
            the_date=THE_DATE,
        )

    save_(THE_DATE)
    
    print_(THE_DATE)   # prints to terminal

    return redirect('/home')


##################################################################
# Homepage and error pages


@app.route('/', methods=["GET", "POST"])
def route():
    """Show welcome page"""

    if g.user:
        THE_DATE = date.today()
        save_(THE_DATE)
        return redirect('/home')
    else:
        return render_template('home-anon.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    return render_template('/errors/404.html'), 404


@app.route('/test')
def show_test():
    """ A test route to print all os.environ data on the terminal
    """

    print("#"*30)
    # print(os.environ)
    print(type(os.environ))
    print("#"*30)
    [print(f"{k}  ==>>  {v}") for k,v in os.environ.items()]
    print("#"*30)

    return "X"
