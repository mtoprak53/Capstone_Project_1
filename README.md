# Calorie Counter Web Application

The [Calorie Counter](https://calorie-counter.herokuapp.com/) web app lets users sign-up and saves their food intake logs day by day. It connects to [Fatsecret API](https://platform.fatsecret.com/api/) for detailed food nutrient information and saves them in the app's own database whenever a food log for that food item is created. Users can create their food intake logs for any day, change the date to reach earlier logs, and edit or delete already created logs for any day. Also, the daily log calculates and shows the user's daily calorie intake.

The UI is designed as two main columns where the left one is populated with control forms and buttons, and the right column is used as the informative part of the page.

There is a "most frequently eaten 20 foods" feature in the app to reach the frequent foods' info easier and directly from the local database (without external API communication).

The back-end of the app is written in Flask (Flask-SQLAlchemy, Flask-WTForms, Flask-Bcrypt) with PostgreSQL on the database side.
Jinja is used as the template system on the front-end. The
[pyfatsecret](https://pyfatsecret.readthedocs.io/en/latest/index.html) library is used to overcome too detailed authentication processes of the API communications.
The live app is deployed on Heroku servers.

[The database schema](/static/images/schema.png) contains four tables.  

![DB Schema](https://github.com/mtoprak53/Capstone_Project_1/blob/main/static/images/schema.png?raw=true)


# How to Build & Deploy

## Create the Python Virtual Environment (venv)

Create the virtual environment in the project directory:
### $ `python3 -m venv venv`  
  
Start the virtual environment:  
### $ `source venv/bin/activate`  

## Install the Required Packages

Install the pip packages required to run the app, listed in the requirements file:  
### (venv) $ `pip3 install -r requirements.txt`  

If you encounter a installation problem with requirements.txt file:  
Try requirements_noproblem.txt and install the 'psycopg2-binary' package seperately because of its incompatibility with newer python3 versions:  
### (venv) $ `pip3 install -r requirements_noproblem.txt`  
### (venv) $ `pip3 install psycopg2-binary`  

## Set up the Database  

Create the database:  
### (venv) $`createdb calorie_db`  

Create the tables:  
### (venv) $`python3 seed.py`  

## Check the App  

Start the app:  
### (venv) $`flask run`  

View it in your browser:  
### [http://localhost:5000](http://localhost:5000)  


```%info
IMPORTANT INFO: For API functionality, a hidden.py file containing working CONSUMER_KEY and CONSUMER_SECRET information from the Fatsecret platform is required. The API functionality can be accessed from the app's website:
```
### [https://calorie-counter.up.railway.app](https://calorie-counter.up.railway.app)



Stop the virtual environment when you finish:  
### (venv) $`deactivate`  


