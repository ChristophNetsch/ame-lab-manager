# -*- coding: utf-8 -*-

from uuid import uuid4

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import (current_user, login_fresh, login_required, login_user,
                         logout_user)
from itsdangerous import URLSafeSerializer

from ..emails import send_async_email
from ..equipment import FilterEquipmentForm, SearchEquipmentForm
from ..extensions import db, login_manager
from ..user import ACTIVE, Users
from .forms import (ChangePasswordForm, ContactUsForm, LoginForm,
                    RecoverPasswordForm, SignupForm)
from .models import ContactUs
from ame_manager_app.equipment.models import EquipmentModel, StorageModel, RoomModel, UsageModel, LocationUsageModel

frontend = Blueprint("frontend", __name__)


@frontend.route("/dashboard")
@login_required
def dashboard():
    _usages = UsageModel.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard/dashboard.html", 
        usages = _usages,
        user = current_user,
        _active_dash=True,
    )
    
@frontend.route("/")
def index():
    # current_app.logger.debug('debug')

    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))

    return render_template("frontend/landing.html", _active_home=True)


@frontend.route("/contact-us", methods=["GET", "POST"])
def contact_us():
    form = ContactUsForm()

    if form.validate_on_submit():
        _contact = ContactUs()
        form.populate_obj(_contact)
        db.session.add(_contact)
        db.session.commit()

        flash("Thanks! We'll get back to you shortly!", "success")

        return redirect(url_for("frontend.contact_us"))

    return render_template("frontend/contact_us.html", form=form)


@frontend.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.index"))

    form = LoginForm(
        login=request.args.get("login", None), next=request.args.get("next", None)
    )

    if form.validate_on_submit():
        
        user, authenticated = Users.authenticate(form.login.data, form.password.data)

        if user and authenticated:

            if user.status_code != 2:
                flash("Please verify your email address to continue", "danger")
                return redirect(url_for("frontend.login"))

            remember = request.form.get("remember") == "y"

            if login_user(user, remember=remember):
                flash("Logged in", "success")
            return redirect(form.next.data or url_for("frontend.index"))
        else:
            flash("Sorry, invalid login", "danger")

    return render_template("frontend/login.html", form=form, _active_login=True)


@frontend.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for("frontend.index"))


@frontend.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("frontend.dashboard"))

    form = SignupForm(next=request.args.get("next"))

    if form.validate_on_submit():
        user = Users()
        user.status_code = 2
        user.name_short = form.name_short.data
        user.email = form.email.data.lower()
        user.account_type = 0
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        confirm_user_mail(form.name.data, form.email.data)

        flash(
            "Confirmation email sent to " + form.email.data + " Please verify!",
            "success",
        )
        return redirect(url_for("frontend.login"))

    return render_template("frontend/signup.html", form=form, _active_signup=True)


def confirm_user_mail(name, email):
    s = URLSafeSerializer("serliaizer_code")
    key = s.dumps([name, email])

    subject = "Confirm your account for " + current_app.config["PROJECT_NAME"]
    url = url_for("frontend.confirm_account", secretstring=key, _external=True)
    html = render_template(
        "macros/_confirm_account.html",
        project=current_app.config["PROJECT_NAME"],
        url=url,
    )

    send_async_email(subject, html, email)


@frontend.route("/confirm_account/<secretstring>", methods=["GET", "POST"])
def confirm_account(secretstring):
    s = URLSafeSerializer("serliaizer_code")
    uname, uemail = s.loads(secretstring)
    user = Users.query.filter_by(name=uname).first()
    user.status_code = ACTIVE
    db.session.add(user)
    db.session.commit()
    flash("Your account was confirmed succsessfully!!!", "success")
    return redirect(url_for("frontend.login"))


@frontend.route("/change_password", methods=["GET", "POST"])
def change_password():

    if current_user.is_authenticated:
        if not login_fresh():
            return login_manager.needs_refresh()

    form = ChangePasswordForm(
        email_activation_key=request.values["email_activation_key"],
        email=request.values["email"],
    )

    if form.validate_on_submit():
        update_password(
            form.email.data, form.email_activation_key.data, form.password.data
        )
        flash("Your password has been changed, log in again", "success")
        return redirect(url_for("frontend.login"))

    return render_template("frontend/change_password.html", form=form)


def update_password(email, email_activation_key, password):
    user = Users.query.filter_by(
        email_activation_key=email_activation_key, email=email
    ).first()
    user.password = password
    user.email_activation_key = None
    db.session.add(user)
    db.session.commit()


@frontend.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    form = RecoverPasswordForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user:
            flash(
                "Please see your email for instructions on how to access your account",
                "success",
            )

            user.email_activation_key = str(uuid4())
            db.session.add(user)
            db.session.commit()

            subject = "Reset your password in " + current_app.config["PROJECT_NAME"]
            url = url_for(
                "frontend.change_password",
                email=user.email,
                email_activation_key=user.email_activation_key,
                _external=True,
            )
            html = render_template(
                "macros/_reset_password.html",
                project=current_app.config["PROJECT_NAME"],
                name=user.name,
                url=url,
            )

            send_async_email(subject, html, user.email)

            return render_template("frontend/reset_password.html", form=form)
        else:
            flash("Sorry, no user found for that email address", "danger")

    return render_template("frontend/reset_password.html", form=form)


@frontend.route("/terms")
def terms():
    return "To be updated soon.."


@frontend.route("/about-us")
def about_us():
    return "To be updated soon.."