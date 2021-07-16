# PYTHON MODULES
import os
from datetime import date, timedelta

# FLASK MODULES
from flask import Flask, redirect, render_template, request, flash, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError   # for already taken usernames

# SPECIAL MODULES
from fatsecret import Fatsecret

# MY MODULES
from forms import UserAddForm, LoginForm
from models import db, connect_db, Food, FoodInfo, FoodLog, User, UserInfo
from hidden import CONSUMER_KEY, CONSUMER_SECRET, DATABASE_URL

# TODAY = date.today()

# CREATE SESSION KEYS
CURR_USER_KEY = "curr_user"
DATE_KEY = "the_date"
# SEARCH_KEY = "search_term"
# PAGE_NUM_KEY = "page_num"
FOOD_KEY = "food"

# BASE_URL = "https://platform.fatsecret.com/rest/server.api"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get(DATABASE_URL, "postgresql:///calorie_db_2")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
# app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", API_SECRET_KEY)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "top_secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

fs = Fatsecret(CONSUMER_KEY, CONSUMER_SECRET)

# db.drop_all()
# db.create_all()


####################################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():   # WHERE IS THIS USED?
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


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If  there already is a user with that username: flash message and re-present the form.
    """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():   # .validate_on_submit()
        try:
            user = User.signup(   # .signup()
                username=form.username.data,
                password=form.password.data
                # first_name=form.first_name.data,
                # last_name=form.last_name.data,
            )
            db.session.commit()
            user_info = UserInfo(
                user_id=user.id,
                calorie_need=form.calorie_need.data,
                calorie_limit=form.calorie_limit.data                
            )
            db.session.add(user_info)
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)
        
        do_login(user)   # do_login()

        return redirect('/')
    
    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():   # .validate_on_submit()
        user = User.authenticate(   # .authenticate()
            form.username.data,
            form.password.data
        )

        if user:
            do_login(user)   # do_login()
            flash(f"Hello, {user.username}!", 'success')
            return redirect('/')

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()   # do_logout

    flash("You have successfully logged out.", 'success')
    return redirect("/login")


####################################################################################
# 

@app.route('/home', methods=["GET", "POST"])
def homepage():
    """We start here!"""

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    # BUILD THE EATEN LIST IF THERE IS ANY LOG
    if FoodLog.query.filter(
        FoodLog.user_id == g.user.id,
        FoodLog.date == THE_DATE
    ).count() > 0:
        dates_foodlog = FoodLog.query.filter(
                        FoodLog.user_id == g.user.id,
                        FoodLog.date == THE_DATE
                    ).all()

        for df in dates_foodlog:
            df.calories = round(df.calories)

        calorie_list = [df.calories for df in dates_foodlog]
        calorie_sum = sum(calorie_list)

        calorie_limit = g.user.userinfo[0].calorie_limit 
        calorie_need = g.user.userinfo[0].calorie_need

        return render_template(
            'home.html', 
            user=g.user, 
            today=TODAY, 
            the_date=THE_DATE, 
            foodlog=dates_foodlog,
            calorie_sum=calorie_sum,
            calorie_limit=calorie_limit,
            calorie_need=calorie_need,
        )

    calorie_sum = 0
    calorie_limit = g.user.userinfo[0].calorie_limit 
    calorie_need = g.user.userinfo[0].calorie_need

    return render_template(
        'home.html', 
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE, 
        calorie_sum=calorie_sum,
        calorie_limit=calorie_limit,
        calorie_need=calorie_need,
    )


@app.route('/food/search', methods=["POST"])
def search_food():
    """Redirect the search term as a query to the next route."""

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    food = request.form["food"]
    try:
        food_list = fs.foods_search(food)

    except:
        return render_template(
            'error_food.html', 
            user=g.user, 
            today=TODAY, 
            the_date=THE_DATE, 
            search_term=food, 
        )

    else:
        return redirect(f"/food/search/{food}/{0}")


@app.route('/food/search/<food>/<int:page_num>')
def search_food_redirect(food, page_num):
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    # FORM THE 10 PAGE LINKS LIST (HIDDEN) ###########
    if page_num < 5:
        pages = range(1,10)
    else:
        pages = range(page_num-3, page_num+6)
    ##################################################

    max_results = 20
    
    food_list = fs.foods_search(
        food, 
        page_number=page_num, 
        max_results=max_results
    )

    try:
        # MANY RESULTS
        food_list[0].get('food_id')

    except:
        # ONLY ONE RESULT
        food_list=[food_list]
    
    return render_template(
        'search_results.html', 
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE,
        food_list=food_list, 
        search_term=food,
        page_number=page_num,
        pages=pages, 
    )


@app.route('/food/add/<int:food_id>', methods=["GET", "POST"])
def add_food(food_id):
    """takes the chosen food and calculates its values
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')
    
    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    # POST
    if request.form:
    
        amount = float(request.form["amount"])
        servings = request.form["servings"]
        foodinfo = session[FOOD_KEY]
        food_id = int(foodinfo['food_id'])

        # DATABASE REGISTERING OF FOOD & ITS INFO #
        if Food.query.get(food_id):

            # IF THE FOOD IS ALREADY IN DATABASE
            pass

        else:

            # IF THE FOOD IS NOT IN DATABASE YET
            if foodinfo.get('brand_name'):
                brand = foodinfo.get('brand_name')
            else:
                brand = 'Generic'

            food = Food(
                id=food_id,
                name=foodinfo['food_name'],
                brand=brand,
                food_url=foodinfo['food_url']
            )

            db.session.add(food)
            db.session.commit()

            serv = foodinfo['servings']['serving']

            # SEND FOOD INFO TO LOCAL DATABASE
            try:
                # ONE SERVING
                serv.get('fat')
                food_info = FoodInfo(food_id=food_id, **serv)
            
                db.session.add(food_info)
                db.session.commit()

            except:
                # LIST SERVING
                for s in serv:
                    food_info = FoodInfo(food_id=food_id, **s)

                    db.session.add(food_info)
                    db.session.commit()
        
        # SEND FOOD-LOG TO DATABASE
        try:
            foodinfo_0 = FoodInfo.query.filter(
                FoodInfo.food_id == food_id,
                FoodInfo.serving_description == servings
            ).one()
        except:
            return render_template(
                        'error_db.html', 
                        user=g.user, 
                        today=TODAY,
                        the_date=THE_DATE, 
                    )

        unit_calories = foodinfo_0.calories
        calories = amount * unit_calories

        if servings == '100 g':
            calories /= 100
        
        foodlog = FoodLog(
            user_id=g.user.id,
            food_id=food_id,
            amount=amount,
            serving_description=servings, 
            unit_calories=unit_calories,
            calories=calories,
        )

        db.session.add(foodlog)
        db.session.commit()

        return redirect('/home')


    # GET
    food_info = fs.food_get(food_id)
    serving_val = food_info['servings']['serving']
    is_it_list = isinstance(serving_val, list)

    # IF THERE IS A LIST OF SERVINGS
    if is_it_list:

        SDs = []
        for serv in serving_val:

            SDs.append(serv['serving_description'])

            if serv['serving_description'] == '100 g':
                unit_amount = serv['serving_description']
                unit_kcal = serv['calories']

    # IF THERE IS ONLY ONE SERVING
    else:
        SDs = [serving_val['serving_description']]
        unit_amount = serving_val['serving_description']
        unit_kcal = serving_val['calories']

    session[FOOD_KEY] = food_info

    return render_template(
        'add_food.html', 
        user=g.user, 
        today=TODAY, 
        the_date=THE_DATE,
        SDs=SDs, 
        unit_kcal=unit_kcal, 
        unit_amount=unit_amount.upper(), 
        food_info=food_info, 
    )


@app.route('/food/log/<int:log_id>/edit', methods=["GET", "POST"])
def edit_food(log_id):
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()
    
    # POST METHOD
    if request.form:
        amount = float(request.form["amount"])

        log = FoodLog.query.get_or_404(log_id)
        log.amount = amount
        log.calories = log.amount * log.unit_calories

        if log.serving_description == '100 g':
            log.calories /= 100

        db.session.commit()

        return redirect('/home')

    # GET METHOD
    log = FoodLog.query.get_or_404(log_id)

    return render_template(
                'edit_food.html',
                user=g.user, 
                the_date=THE_DATE,
                today=TODAY,
                log=log
            )


@app.route('/food/log/<int:log_id>/delete', methods=["POST"])
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


### UNDER CONSTRUCTION ###
@app.route('/food/frequent')
def frequent_foods():
    """
    """

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    # USER'S ALL FOOD-LOGS
    all_logs = FoodLog.query.filter_by(user_id=g.user.id).all()

    # FOOD-IDs OF USER'S FOOD-LOGS
    food_ids = [log.food_id for log in all_logs]
    fid_set = set(food_ids)

    # (FOOD-ID, FREQUENCY) TUPLES LIST
    food_freq = [(fid, FoodLog.query.filter(FoodLog.user_id==g.user.id, FoodLog.food_id==fid).count()) for fid in fid_set]

    # REVERSE SORTED (FOOD-ID, FREQUENCY) TUPLES LIST
    ffs = sorted(food_freq, key=lambda x: x[1], reverse=True)

    fids20 = [t[0] for t in ffs[:20]]

    # fidlogs = 

    foodlogs = [FoodLog.query.filter(FoodLog.user_id==g.user.id, FoodLog.food_id==fid).all() for fid in fids20]



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

        the_date = request.form["chosen_date"]
        save_(the_date)

        return redirect('/home')

    return render_template(
        'choose_date.html', 
        user=g.user, 
        today=TODAY,
        the_date=THE_DATE,
    )


@app.route('/day-change/<direction>/<int:days>')
def change_day(direction, days):
    """X"""

    # CHECK IF THE USER LOGGED IN
    if not session.get(CURR_USER_KEY):
        return redirect('/')

    # FIND OUT THE DATE
    TODAY = date.today()
    THE_DATE = load_the_date()

    t1 = timedelta(days)
    if direction == 'post':
        THE_DATE += t1
    elif direction == 'pre':
        THE_DATE -= t1
    else:
        return render_template(
            '/error_date.html',
            user=g.user, 
            today=TODAY,
            the_date=THE_DATE,
        )

    save_(THE_DATE)

    return redirect('/home')


####################################################################################
# 


####################################################################################
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

    return render_template('404.html'), 404


####################################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"    
#     req.headers["Cache-Control"] = "public, max-age=0"
#     return req
