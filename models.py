"""SQLAlchemy models for Calorie Counter"""

from datetime import date
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

###########################################################
# DATABASE MODELS:


class FoodLog(db.Model):
    """Each food consumption entry."""

    __tablename__ = 'foodlogs'

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    food_id = db.Column(
        db.Integer,
        db.ForeignKey('foods.id', ondelete="cascade")
    )

    amount = db.Column(
        db.Float(1),
        nullable=False
    )

    serving_description = db.Column(
        db.Text,
        nullable=False
    )

    unit_calories = db.Column(
        db.Float, 
        nullable=False
    )

    calories = db.Column(
        db.Float(2),
        nullable=False
    )

    date = db.Column(
        db.Date,
        nullable=False,
        default=date.today().isoformat()
    )

    user = db.relationship('User', backref='foodlog')

    food = db.relationship('Food', backref='foodlog')


class Food(db.Model):
    """Info of the foods."""

    __tablename__ = 'foods'

    id = db.Column(
        db.Integer,
        primary_key=True,
        # autoincrement=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    brand = db.Column(
        db.Text,
        nullable=False,
        default = "Generic"
    )

    food_url = db.Column(
        db.Text,        
    )

    def __repr__(self):

        return f"Food Name: {self.name}, Type: {self.brand}"


class FoodInfo(db.Model):
    """Food servings."""

    __tablename__ = 'foodinfos'

    # 01
    food_id = db.Column(
        db.Integer,
        db.ForeignKey('foods.id', ondelete="cascade"),
        primary_key=True
    )

    # 02
    calcium = db.Column(
        db.String,
    )

    # 03
    calories = db.Column(
        db.Float,
    )

    # 04
    carbohydrate = db.Column(
        db.Float,
    )

    # 05
    cholesterol = db.Column(
        db.Float,
    )

    # 06
    fat = db.Column(
        db.Float,
    )

    # 07
    fiber = db.Column(
        db.Float,
    )

    # 08
    iron = db.Column(
        db.Float,
    )

    # 09
    measurement_description = db.Column(
        db.String,
    )

    # 10
    metric_serving_amount = db.Column(
        db.String,
    )

    # 11
    metric_serving_unit = db.Column(
        db.String,
    )

    # 12
    monounsaturated_fat = db.Column(
        db.Float,
    )

    # 13
    number_of_units = db.Column(
        db.String,
    )

    # 14
    polyunsaturated_fat = db.Column(
        db.Float,
    )

    # 15
    potassium = db.Column(
        db.Float,
    )

    # 16
    protein = db.Column(
        db.Float,
    )

    # 17
    saturated_fat = db.Column(
        db.Float,
    )

    # 18
    serving_description = db.Column(
        db.String,
        primary_key=True,
    )

    # 19
    serving_id = db.Column(
        db.String,
    )

    # 20
    serving_url = db.Column(
        db.String,
    )

    # 21
    sodium = db.Column(
        db.Float,
    )

    # 22
    sugar = db.Column(
        db.Float,
    )

    # 23
    trans_fat = db.Column(
        db.Float,
    )

    # 24
    vitamin_a = db.Column(
        db.Float,
    )

    # 25
    vitamin_c = db.Column(
        db.Float,
    )

    foods = db.relationship(
        'Food', 
        backref='foodinfo',
        cascade="all, delete"
    ) 

    def __repr__(self):

        return f"FoodInfo for Food #{self.food_id} & serving description {self.serving_description} "


class UserInfo(db.Model):
    """User details."""

    __tablename__ = 'userinfos'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )

    calorie_limit = db.Column(
        db.Integer,
        nullable=False
    )

    calorie_need = db.Column(
        db.Integer,
        nullable=False
    )

    user = db.relationship('User', backref="userinfo")


class User(db.Model):
    """User credentials."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )




    ###   MODIFY THIS   ###
    # def __repr__(self):
    #     """Show info about the user."""
        
    #     return f"<User #{self.id}: {self.username}, {self.password}>"


    @classmethod
    def signup(cls, username, password):
        """
        Signup user.
        Hashes password and adds user to the system.
        """

        # .generate_password_hash()
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """
        Find user with `username` & `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password,
        and if it finds such a user, returns that user object.
        If it cannot find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            # .check_password_hash()
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    

###########################################################
# MY FUNCTIONS:

# def find_the_date(DATE_KEY, TODAY, session):
#     """
#     IF ANOTHER DATE IS BEING MODIFIED
#     session[DATE_KEY] HAS IT AS ISO
#     IF TODAY IS BEING MODIFIED session[DATE_KEY] IS EMPTY
#     THE_DATE HAS THE DATE HAS BEEN MODIFIED
#     """

#     if DATE_KEY in session:
#         return date.fromisoformat(session[DATE_KEY])
#     else:
#         return TODAY
    




###########################################################
# DATABASE CONNECTION:

def connect_db(app):
    """Database connection function."""

    db.app = app
    db.init_app(app)
