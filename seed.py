from app import db
# from models import FoodLog, Food, FoodServing, User

db.drop_all()
db.create_all()