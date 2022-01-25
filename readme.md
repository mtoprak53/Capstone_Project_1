# Calorie Counter Web Application

[Calorie Counter web app](https://serene-ridge-82147.herokuapp.com) lets users signup and save their food intake logs day by day. It connects to [Fatsecret API](https://platform.fatsecret.com/api/) for detailed food nutrient information and saves them in the app's own database whenever a food log for that food item is created. Users can create their food intake logs for any day, change the date to reach earlier logs, and edit or delete already created logs for any day. Also, the daily log calculates and shows the user's daily calorie intake.

The UI is designed as two main columns where the left one is populated with control forms and buttons, and the right column is used as the informative part of the page.

There is a "most frequent eaten 20 foods" feature in the app to reach the frequent foods' info easier and directly from the local database (without external API communication).

The back-end of the app is written in Flask (Flask-SQLAlchemy, Flask-WTForms, Flask-Bcrypt) with PostgreSQL at the database side.
Jinja is used as the template system on the front-end.
[pyfatsecret](https://pyfatsecret.readthedocs.io/en/latest/index.html) library is used to overcome too detailed authentication processes of the API communications.
The live app is deployed on Heroku servers.

[The database schema](/static/images/schema.png) contains four tables.




