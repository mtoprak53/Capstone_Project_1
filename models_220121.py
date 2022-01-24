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

    food_log = db.relationship('FoodLog', 
                                backref='food',
                                # cascade="all, delete"
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

    food_log = db.relationship('FoodLog',
                                cascade="all, delete", 
                                backref='user')

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


apple = {'food_id': '35718',
 'food_name': 'Apples',
 'food_type': 'Generic',
 'food_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples',
 'servings': {'serving': [{'calcium': '1',
    'calories': '65',
    'carbohydrate': '17.26',
    'cholesterol': '0',
    'fat': '0.21',
    'fiber': '3.0',
    'iron': '1',
    'measurement_description': 'cup, quartered or chopped',
    'metric_serving_amount': '125.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.009',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.064',
    'potassium': '134',
    'protein': '0.32',
    'saturated_fat': '0.035',
    'serving_description': '1 cup quartered or chopped',
    'serving_id': '32912',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32912&portionamount=1.000',
    'sodium': '1',
    'sugar': '12.99',
    'vitamin_a': '0',
    'vitamin_c': '6'},
   {'calcium': '1',
    'calories': '57',
    'carbohydrate': '15.19',
    'cholesterol': '0',
    'fat': '0.19',
    'fiber': '2.6',
    'iron': '1',
    'measurement_description': 'cup slices',
    'metric_serving_amount': '110.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.008',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.056',
    'potassium': '118',
    'protein': '0.29',
    'saturated_fat': '0.031',
    'serving_description': '1 cup slices',
    'serving_id': '32913',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32913&portionamount=1.000',
    'sodium': '1',
    'sugar': '11.43',
    'vitamin_a': '0',
    'vitamin_c': '6'},
   {'calcium': '1',
    'calories': '110',
    'carbohydrate': '29.28',
    'cholesterol': '0',
    'fat': '0.36',
    'fiber': '5.1',
    'iron': '1',
    'measurement_description': 'large (3-1/4" dia) (approx 2 per lb)',
    'metric_serving_amount': '212.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.015',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.108',
    'potassium': '227',
    'protein': '0.55',
    'saturated_fat': '0.059',
    'serving_description': '1 large (3-1/4" dia) (approx 2 per lb)',
    'serving_id': '32914',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32914&portionamount=1.000',
    'sodium': '2',
    'sugar': '22.03',
    'vitamin_a': '1',
    'vitamin_c': '11'},
   {'calcium': '1',
    'calories': '72',
    'carbohydrate': '19.06',
    'cholesterol': '0',
    'fat': '0.23',
    'fiber': '3.3',
    'iron': '1',
    'measurement_description': 'medium (2-3/4" dia) (approx 3 per lb)',
    'metric_serving_amount': '138.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.010',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.070',
    'potassium': '148',
    'protein': '0.36',
    'saturated_fat': '0.039',
    'serving_description': '1 medium (2-3/4" dia) (approx 3 per lb)',
    'serving_id': '32915',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32915&portionamount=1.000',
    'sodium': '1',
    'sugar': '14.34',
    'vitamin_a': '0',
    'vitamin_c': '7'},
   {'calcium': '0',
    'calories': '55',
    'carbohydrate': '14.64',
    'cholesterol': '0',
    'fat': '0.18',
    'fiber': '2.5',
    'iron': '1',
    'measurement_description': 'small (2-1/2" dia) (approx 4 per lb)',
    'metric_serving_amount': '106.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.007',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.054',
    'potassium': '113',
    'protein': '0.28',
    'saturated_fat': '0.030',
    'serving_description': '1 small (2-1/2" dia) (approx 4 per lb)',
    'serving_id': '32916',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32916&portionamount=1.000',
    'sodium': '1',
    'sugar': '11.01',
    'vitamin_a': '0',
    'vitamin_c': '5'},
   {'calcium': '1',
    'calories': '80',
    'carbohydrate': '21.27',
    'cholesterol': '0',
    'fat': '0.26',
    'fiber': '3.7',
    'iron': '1',
    'measurement_description': 'NLEA serving',
    'metric_serving_amount': '154.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.011',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.079',
    'potassium': '165',
    'protein': '0.40',
    'saturated_fat': '0.043',
    'serving_description': '1 NLEA serving',
    'serving_id': '32917',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=32917&portionamount=1.000',
    'sodium': '2',
    'sugar': '16.00',
    'vitamin_a': '1',
    'vitamin_c': '8'},
   {'calcium': '0',
    'calories': '15',
    'carbohydrate': '3.92',
    'cholesterol': '0',
    'fat': '0.05',
    'fiber': '0.7',
    'iron': '0',
    'measurement_description': 'oz',
    'metric_serving_amount': '28.350',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.002',
    'number_of_units': '1.000',
    'polyunsaturated_fat': '0.014',
    'potassium': '30',
    'protein': '0.07',
    'saturated_fat': '0.008',
    'serving_description': '1 oz',
    'serving_id': '43637',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=43637&portionamount=1.000',
    'sodium': '0',
    'sugar': '2.95',
    'vitamin_a': '0',
    'vitamin_c': '1'},
   {'calcium': '0',
    'calories': '52',
    'carbohydrate': '13.81',
    'cholesterol': '0',
    'fat': '0.17',
    'fiber': '2.4',
    'iron': '1',
    'measurement_description': 'g',
    'metric_serving_amount': '100.000',
    'metric_serving_unit': 'g',
    'monounsaturated_fat': '0.007',
    'number_of_units': '100.000',
    'polyunsaturated_fat': '0.051',
    'potassium': '107',
    'protein': '0.26',
    'saturated_fat': '0.028',
    'serving_description': '100 g',
    'serving_id': '58449',
    'serving_url': 'https://www.fatsecret.com/calories-nutrition/usda/apples?portionid=58449&portionamount=100.000',
    'sodium': '1',
    'sugar': '10.39',
    'vitamin_a': '0',
    'vitamin_c': '5'}]}}