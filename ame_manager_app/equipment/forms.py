# -*- coding: utf-8 -*-

from random import choices
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, IntegerField, DateField, DateTimeLocalField, DateTimeField, SelectField
from wtforms.validators import DataRequired,InputRequired, Length, NumberRange
from ..utils import get_current_time
from ame_manager_app.equipment.models import EquipmentModel

from ame_manager_app.config import DefaultConfig

class BorrowEquipmentForm(FlaskForm):
    borrowing_equipment = SelectField(validators=[DataRequired()])
    user = SelectField(validators=[DataRequired()])
    name = StringField("Usage name", validators=[DataRequired(), Length(5, 2048)])
    usage_start_datetime = DateTimeField("Usage start date", validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    #alt1_usage_planned_end_date = DateField("Planned usage end as A) date...")
    alt2_usage_duration_days = IntegerField("...or alternative as B) duration in days", validators=[DataRequired()])
    usage_location_id = SelectField(validators=[DataRequired()])
    submit = SubmitField("Borrow")

class SearchEquipmentForm(FlaskForm):
    name = StringField("Usage Name", [Length(5, 2048)])
    storage_location = StringField("Storage Location", [Length(5, 2048)])
    room = StringField("Room", [Length(5, 2048)])
    submit = SubmitField("Search")