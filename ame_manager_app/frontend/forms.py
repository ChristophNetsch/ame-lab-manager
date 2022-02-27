# -*- coding: utf-8 -*-

from flask import Markup
from flask_wtf import FlaskForm
from wtforms import (BooleanField, EmailField, HiddenField, PasswordField,
                     StringField, SubmitField, TextAreaField, ValidationError)
from wtforms.validators import Email, EqualTo, InputRequired, Length

from ..user import Users
from ..utils import (NAME_LEN_MAX, NAME_LEN_MIN, PASSWORD_LEN_MAX,
                     PASSWORD_LEN_MIN)

terms_html = Markup('<a target="blank" href="/terms">Terms of Service</a>')


class LoginForm(FlaskForm):
    next = HiddenField()
    login = StringField("Email", [InputRequired()])
    password = PasswordField(
        "Password", [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)]
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class SignupForm(FlaskForm):
    next = HiddenField()
    name = StringField("Name", [InputRequired(), Length(NAME_LEN_MIN, NAME_LEN_MAX)])
    email = EmailField("Email", [InputRequired(), Email()])
    password = PasswordField(
        "Password",
        [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
        description=" 6 or more characters.",
    )
    agree = BooleanField("Agree to the " + terms_html, [InputRequired()])
    submit = SubmitField("Sign up")

    def validate_email(self, field):
        if Users.query.filter_by(email=field.data).first() is not None:
            raise ValidationError("This email is taken")


class RecoverPasswordForm(FlaskForm):
    email = EmailField("Your email", [Email()])
    submit = SubmitField("Send instructions")


class ChangePasswordForm(FlaskForm):
    email_activation_key = HiddenField()
    email = HiddenField()
    password = PasswordField("Password", [InputRequired()])
    password_again = PasswordField(
        "Password again", [EqualTo("password", message="Passwords don't match")]
    )
    submit = SubmitField("Save")


class ContactUsForm(FlaskForm):
    name = StringField("Name", [InputRequired(), Length(max=64)])
    email = EmailField("Your Email", [InputRequired(), Email(), Length(max=64)])
    subject = StringField("Subject", [InputRequired(), Length(5, 128)])
    message = TextAreaField("Your Message", [InputRequired(), Length(10, 1024)])
    submit = SubmitField("Submit")
