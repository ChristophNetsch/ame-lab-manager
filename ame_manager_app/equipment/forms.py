# -*- coding: utf-8 -*-

from random import choices
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, RadioField, StringField, IntegerField, DateField, DateTimeLocalField, DateTimeField, SelectField
from wtforms.validators import DataRequired,InputRequired, Length, NumberRange,Optional
from ..utils import get_current_time
from ame_manager_app.equipment.models import EquipmentModel

from ame_manager_app.config import DefaultConfig

class BorrowEquipmentForm(FlaskForm):
    borrowing_equipment = SelectField(validators=[DataRequired()])
    user = SelectField(validators=[DataRequired()])
    name = StringField("Usage name", validators=[DataRequired(), Length(5, 2048)])
    usage_start_datetime = DateTimeField("Usage start date", validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    alt1_usage_planned_end_date = DateField("Planned usage end")
    #alt2_usage_duration_days = IntegerField("Planned usage duration in days")
    usage_location_id = SelectField(validators=[DataRequired()])
    submit = SubmitField("Borrow")

class FilterEquipmentForm(FlaskForm):
    room = SelectField("Storage room", validators=[Optional()])
    storage_location = SelectField("Storage location", validators=[Optional()])
    usage_location = SelectField("Usage location", validators=[Optional()])
    filter_mode = RadioField("Choose filter", validators=[DataRequired()])
    submit = SubmitField("Filter")

class SearchEquipmentForm(FlaskForm):
    equipment_id = SelectField("Equipment",validators=[DataRequired()])
    submit = SubmitField("Search")
    
class AddCommentForm(FlaskForm):
    equipment_id = SelectField("Equipment",validators=[DataRequired()])
    comment = StringField("Comment Text", [Length(5, 2048)])
    submit = SubmitField("Submit")

class AddCalibrationForm(FlaskForm):
    equipment_id = SelectField("Equipment",validators=[DataRequired()])
    date = DateTimeField("Calibration date", validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    date_until = DateField("Calibration end date")
    comment = StringField("Calibration text (optional)")
    submit = SubmitField("Submit")
    
class AddBriefingForm(FlaskForm):
    equipment_id = SelectField("Equipment",validators=[DataRequired()])
    briefer_id = SelectField("Briefing user",validators=[DataRequired()])
    briefed_user_id = SelectField("Briefed user",validators=[DataRequired()])
    date = DateTimeField("Date of briefing",validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    text = StringField("Briefing text (optional)")
    date_until= DateField("Briefing expiry date (optional)",validators=(Optional(),))
    submit = SubmitField("Submit")