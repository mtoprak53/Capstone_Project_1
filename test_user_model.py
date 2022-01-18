"""User model tests"""

# run like:

#     python -m unittest -v test_user_model.py

import os
from unittest import TestCase, expectedFailure

from models import db, User, Food, FoodLog, FoodServing

# os.environ['DATABASE_URL'] = "postgresql:///calorie_db_test"
os.environ['HEROKU_POSTGRESQL_IVORY_URL'] = "postgresql:///calorie_db_test"

from app import app

db.create_all()


TEST_USER_1 = {
    "username": "test_user_1",
    "password": "test_password_1",
    "calorie_need": 2200,
    "calorie_limit": 1850,
}

TEST_USER_2 = {
    "username": "test_user_2",
    "password": "test_password_2",
    "calorie_need": 2500,
    "calorie_limit": 2050,
}

class UserModelTestCase(TestCase):
    """Test models for users"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        user_1 = User(**TEST_USER_1)
        user_2 = User(**TEST_USER_2)
        db.session.add_all([user_1, user_2])
        db.session.commit()

        self.user_1 = user_1
        self.user_2 = user_2

    def tearDown(self):
        """Clean up fouled transaction"""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            username="test_user",
            password="test_password",
            calorie_need=2350,
            calorie_limit=2100
        )

        db.session.add(u)
        db.session.commit()

        # User should have no foodlogs
        self.assertEqual(len(u.foodlog), 0)

    def test_user_repr_method(self):
        """Does repr method work as expected?"""

        self.assertIn("<User #", repr(self.user_1))
        self.assertIn(": test_user_1", repr(self.user_1))
        self.assertIn("<User #", repr(self.user_2))
        self.assertIn(": test_user_2", repr(self.user_2))

    def test_user_signup_success(self):
        """Does signup class method work as expected at success?"""

        signedup_user = User.signup(username="testuser",
                                    password="testpassword",
                                    calorie_need=2600,
                                    calorie_limit=2300)

        db.session.commit()

        testuser = User.query.filter_by(username="testuser").one()

        self.assertEqual(signedup_user, testuser)

        self.assertEqual(User.query.count(), 3)


    @expectedFailure
    def test_user_signup_fail_1(self):
        """Does signup class method work as expected at fail?"""

        User.signup(username="testuser",
                    password="testpassword",
                    calorie_need=None,        # shouldn't be null
                    calorie_limit=2300)

        db.session.commit()


    @expectedFailure
    def test_user_signup_fail_2(self):
        """Does signup class method work as expected at fail?"""

        User.signup(username="testuser",
                    password="testpassword",
                    calorie_need=2600,
                    calorie_limit=None)        # shouldn't be null

        db.session.commit()


    @expectedFailure
    def test_user_signup_fail_3(self):
        """Does signup class method work as expected at fail?"""

        User.signup(username="test_user_1",    # existing username
                    password="testpassword",
                    calorie_need=2600,
                    calorie_limit=2300)

        db.session.commit()


    def test_user_authenticate(self):
        """Does authenticate class method work as expected?"""

        user = User.signup(username="testuser",
                           password="password1234",
                           calorie_need=2600,
                           calorie_limit=2300)

        db.session.commit()

        # Authentication with correct credentials
        auth_user = User.authenticate(username="testuser",
                                      password="password1234")

        self.assertEqual(user, auth_user)

        # Failed authentication with invalid username
        wrong_user = User.authenticate(username="wrong_username",
                                      password="password1234")

        self.assertNotEqual(user, wrong_user)

        # Failed authentication with invalid password
        wrong_pass = User.authenticate(username="testuser",
                                      password="wrong_password")

        self.assertNotEqual(user, wrong_pass)
