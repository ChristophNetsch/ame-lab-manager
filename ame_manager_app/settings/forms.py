# -*- coding: utf-8 -*-

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (EmailField, PasswordField, StringField, SubmitField,
                     ValidationError)
from wtforms.validators import Email, EqualTo, InputRequired, Length

from ..user import Users
from ..utils import PASSWORD_LEN_MAX, PASSWORD_LEN_MIN


class ProfileForm(FlaskForm):
    multipart = True
    name = StringField("Name", [Length(max=50)])
    email = EmailField("Email", [InputRequired(), Email()])
    submit = SubmitField("Update")


class PasswordForm(FlaskForm):
    password = PasswordField("Current password", [InputRequired()])
    new_password = PasswordField(
        "New password", [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)]
    )
    password_again = PasswordField(
        "Password again",
        [
            InputRequired(),
            Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX),
            EqualTo("new_password"),
        ],
    )
    submit = SubmitField("Update")

    def validate_password(form, field):
        user = Users.get_by_id(current_user.id)
        if not user.check_password(field.data):
            raise ValidationError("Password is wrong")
