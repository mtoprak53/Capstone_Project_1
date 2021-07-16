from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Optional, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[InputRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)]
    )

    # first_name = StringField(
    #     'First Name',
    #     validators=[Optional()]
    # )

    # last_name = StringField(
    #     'Last Name',
    #     validators=[Optional()]
    # )

    calorie_need = IntegerField(
        'Daily Calorie Need',
        validators=[InputRequired()]
    )

    calorie_limit = IntegerField(
        'Daily Calorie Limit',
        validators=[InputRequired()]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)]
    )






















