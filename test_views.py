"""User View tests"""

# run like:
#
#   FLASK_ENV=production python -m unittest -v test_views.py

import os
from datetime import date
from unittest import TestCase

from models import db, connect_db, User, Food, FoodLog, FoodServing, apple

os.environ['DATABASE_URL'] = "postgresql:///calorie_db_test"
# os.environ['HEROKU_POSTGRESQL_IVORY_URL'] = "postgresql:///calorie_db_test"

from app import app, FOOD_KEY, CURR_USER_KEY, DATE_KEY, yaz, print_

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] =['dont-show-debug-toolbar'] 

# make WTF does not use CSRF for tests 
app.config['WTF_CSRF_ENABLED'] = False


db.drop_all()
db.create_all()


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

        # TEST FOOD
        self.apple = apple
        self.food_id = int(apple['food_id'])
        # self.food_id = apple['food_id']
        self.food_name = apple['food_name']
        self.serving = [s for s in apple['servings']['serving'] if s['measurement_description'] == 'g'][0]
        self.serving_id = int(self.serving['serving_id'])
        # self.serving_id = self.serving['serving_id']

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transaction"""

        db.session.rollback()

    # ADD FOOD
    def test_food_add(self):
        """Can we add foods?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            resp = c.post(f"/food/add/{self.food_id}",
                        data={"amount": 100, 
            "servings": f"({self.food_id}, {self.serving_id})"},
            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.food_name, html)


    # ADD FOOD - ANONYMOUS
    def test_food_add_anonymous(self):
        """Is anonymous user prevented from adding foodlogs?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()
                if sess.get(CURR_USER_KEY):
                    del sess[CURR_USER_KEY]

            resp = c.post(f"/food/add/{self.food_id}",
                data={"amount": 100, 
            "servings": f"({self.food_id}, {self.serving_id})"},
            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Get Ready to Get In Shape!", html)
               

    # EDIT FOOD PREP
    def make_a_foodlog(self):
        """Saving our food item to DB to edit later"""

        food = Food(id=self.food_id,
                    name=self.apple['food_name'],
                    brand=self.apple['food_type'],
                    food_url='https://www.fatsecret.com/calories-nutrition/usda/apples')
            
        db.session.add(food)

        self.serving['serving_id'] = int(self.serving['serving_id'])
        adjusted_serving = {'food_id': self.food_id, 
                            'trans_fat': 0, 
                            **self.serving}
        food_serving = FoodServing(**adjusted_serving)

        db.session.add(food_serving)
        db.session.commit()   # THIS COMMIT NEEDED !!
        
        amount = 85
        unit_calories = float(self.serving['calories'])
        number_of_units = float(self.serving['number_of_units'])
        calories = unit_calories * amount / number_of_units

        self.food_log = FoodLog(
            user_id=self.testuser.id,
            food_id=self.food_id,
            serving_id=food_serving.serving_id,
            serving_description=food_serving.serving_description,
            unit_calories=unit_calories,
            number_of_units=number_of_units,
            amount=amount,
            calories=calories,
            date=date.today().isoformat()
        )

        db.session.add(self.food_log)
        db.session.commit()

    # EDIT FOOD
    def test_food_edit(self):
        """Can we edit foods?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            resp = c.post(f"/food/edit/{self.food_log.id}", 
                            data={"amount": 100}, 
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.food_name, html)


    # EDIT FOOD - ANONYMOUS
    def test_food_edit_anonymous(self):
        """Is anonymous user prevented from editing foodlogs?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            # TO AVOID DetachedInstanceError AT POST METHOD
            log_id = self.food_log.id

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            resp = c.post(f"/food/edit/{log_id}", 
                            data={"amount": 150}, 
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Get Ready to Get In Shape!", html)


    # EDIT FOOD - NOT AUTHORIZED
    def test_food_edit_unauthorized(self):
        """Is unauthorized user prevented from editing foodlogs?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            # TO AVOID DetachedInstanceError AT POST METHOD
            log_id = self.food_log.id

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999

            resp = c.post(f"/food/edit/{log_id}", 
                            data={"amount": 150}, 
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Get Ready to Get In Shape!", html)


    # DELETE FOOD
    def test_food_delete(self):
        """Can we delete foods?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            resp = c.post(f"/food/delete/{self.food_log.id}",
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(self.food_name, html)
    

    # DELETE FOOD - ANONYMOUS
    def test_food_delete_anonymous(self):
        """Is anonymous user prevented from deleting foodlogs?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            # TO AVOID DetachedInstanceError AT POST METHOD
            log_id = self.food_log.id

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            resp = c.post(f"/food/delete/{log_id}",
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Get Ready to Get In Shape!", html)


    # DELETE FOOD - NOT AUTHORIZED
    def test_food_delete_unauthorized(self):
        """Is unauthorized user prevented from deleting foodlogs?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            self.make_a_foodlog()

            # TO AVOID DetachedInstanceError AT POST METHOD
            log_id = self.food_log.id

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999

            resp = c.post(f"/food/delete/{log_id}",
                            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Get Ready to Get In Shape!", html)

    
    # SEARCH FOOD (CONNECTS TO API?)
    def test_food_add(self):
        """Can we add foods?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess[FOOD_KEY] = apple
                sess[DATE_KEY] = date.today().isoformat()

            resp = c.post(f"/food/add/{self.food_id}",
                        data={"amount": 100, 
            "servings": f"({self.food_id}, {self.serving_id})"},
            follow_redirects=True)
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.food_name, html)

    # CHANGE DATE


