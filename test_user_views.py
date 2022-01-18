"""User View tests"""

# run like:
#
#   FLASK_ENV=production python -m unittest -v test_user_views.py

import os
from unittest import TestCase

from models import db, connect_db, User, Food, FoodLog, FoodServing

# os.environ['DATABASE_URL'] = "postgresql:///calorie_db_test"
os.environ['HEROKU_POSTGRESQL_IVORY_URL'] = "postgresql:///calorie_db_test"

from app import app, CURR_USER_KEY

db.create_all()

# make WTF does not use CSRF for tests 
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    password="testpass123",
                                    calorie_need=2200,
                                    calorie_limit=1850)

        self.testuser_id = 666
        self.testuser.id = self.testuser_id


