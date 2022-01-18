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

    __tablename__ = 'food_logs'

    id = db.Column(
        db.Integer,
        primary_key = True
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"), 
        nullable=False
    )

    food_id = db.Column(
        db.Integer,
        db.ForeignKey('foods.id', ondelete="cascade"), 
        nullable=False
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

    user = db.relationship('User', backref='food_log')

    food = db.relationship('Food', backref='food_log')


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

        return f"Food Name: {self.name} | Type: {self.brand}"


class FoodServing(db.Model):
    """Food servings information received from Fatsecret API"""

    __tablename__ = 'food_servings'

    #############################
    # SERVING INFORMATION

    # 01
    food_id = db.Column(
        db.Integer,
        db.ForeignKey('foods.id', ondelete="cascade"), 
        nullable=False
    )
    
    # 02
    serving_id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # 03
    serving_description = db.Column(
        db.String,
    )

    # 04
    serving_url = db.Column(
        db.String,
    )

    #############################
    # MEASUREMENT INFORMATION

    # 05
    measurement_description = db.Column(
        db.String,
    )

    # 06
    metric_serving_amount = db.Column(
        db.String,
    )

    # 07
    metric_serving_unit = db.Column(
        db.String,
    )

    # 08
    number_of_units = db.Column(
        db.String,
    )

    #############################
    # NUTRIENT INFORMATION

    # 09
    calories = db.Column(
        db.Float,
    )

    # 10
    carbohydrate = db.Column(
        db.Float,
    )

    # 11
    sugar = db.Column(
        db.Float,
    )

    # 12
    fiber = db.Column(
        db.Float,
    )

    # 13
    fat = db.Column(
        db.Float,
    )

    # 14
    protein = db.Column(
        db.Float,
    )

    # 15
    trans_fat = db.Column(
        db.Float,
    )

    # 16
    calcium = db.Column(
        db.String,
    )

    # 17
    cholesterol = db.Column(
        db.Float,
    )

    # 18
    iron = db.Column(
        db.Float,
    )

    # 19
    monounsaturated_fat = db.Column(
        db.Float,
    )

    # 20
    polyunsaturated_fat = db.Column(
        db.Float,
    )

    # 21
    potassium = db.Column(
        db.Float,
    )

    # 22
    saturated_fat = db.Column(
        db.Float,
    )

    # 23
    sodium = db.Column(
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

    # relationships
    food = db.relationship(
        'Food', 
        backref='food_serving',
        cascade="all, delete"
    ) 

    def __repr__(self):

        return f"FoodInfo for Food #{self.food_id} & serving description {self.serving_description} "


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

    calorie_need = db.Column(
        db.Integer,
        nullable=False
    )

    calorie_limit = db.Column(
        db.Integer,
        nullable=False
    )

    def __repr__(self):
        """Show info about the user."""
        
        return f"<User #{self.id}: {self.username}>"


    @classmethod
    def signup(cls, username, password, calorie_need=None, calorie_limit=None):
        """
        Signup user.
        Hashes password and adds user to the system.
        """

        # .generate_password_hash()
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            calorie_need=calorie_need,
            calorie_limit=calorie_limit
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
# DATABASE CONNECTION:

def connect_db(app):
    """Database connection function."""

    db.app = app
    db.init_app(app)
