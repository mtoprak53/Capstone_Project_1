# Calorie Counter Web Application

## What is it

The [Calorie Counter](https://calorie-counter.herokuapp.com/) web app lets users sign-up and saves their food intake logs day by day. It connects to [Fatsecret API](https://platform.fatsecret.com/api/) for detailed food nutrient information and saves them in the app's own database whenever a food log for that food item is created. Users can create their food intake logs for any day, change the date to reach earlier logs, and edit or delete already created logs for any day. Also, the daily log calculates and shows the user's daily calorie intake.

The UI is designed as two main columns where the left one is populated with control forms and buttons, and the right column is used as the informative part of the page.

There is a "most frequently eaten 20 foods" feature in the app to reach the frequent foods' info easier and directly from the local database (without external API communication).

The back-end of the app is written in Flask (Flask-SQLAlchemy, Flask-WTForms, Flask-Bcrypt) with PostgreSQL on the database side.
Jinja is used as the template system on the front-end. The
[pyfatsecret](https://pyfatsecret.readthedocs.io/en/latest/index.html) library is used to overcome too detailed authentication processes of the API communications.
The live app is deployed on Heroku servers.

[The database schema](/static/images/schema.png) contains four tables.



## How to build & deploy
In the project directory, you can run:
### `python3 -m venv venv`
to create the virtual environment.

### `pip3 install -r requirements.txt`
installs the pip packages required to run the app, listed in the requirements file.

### `source venv/bin/activate`
runs the app.

Open [http://localhost:5000](http://localhost:5000) to view it in your browser.

### `deactivate`
stops the app.








