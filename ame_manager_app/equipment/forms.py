# -*- coding: utf-8 -*-

from random import choices
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import BooleanField,SubmitField, SelectMultipleField, SelectField, RadioField, StringField, DateField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from ..utils import get_current_time

class RegisterEquipmentForm(FlaskForm):
    name = StringField("Equipment name", validators=[DataRequired(), Length(5, 2048)])
    info_text = StringField("Info text", validators=[Optional()])
    reference_url = StringField("Reference URL", validators=[Optional()])

    responsible_user = SelectField(validators=[DataRequired()])
    storage_location_id = SelectField("Storage location", validators=[DataRequired()])

    is_usable = BooleanField(" Is usable", validators=[Optional()])
    is_calibration_nessessary = BooleanField(" Calibration for use is necessary", validators=[Optional()])
    is_briefing_nessessary = BooleanField(" Briefing for user is necessary", validators=[Optional()])

    id_lab_CVE = StringField("ID CVE", validators=[Optional()])
    id_lab_UKA = StringField("ID UKA", validators=[Optional()])
    submit = SubmitField("Register")
    
class BorrowEquipmentForm(FlaskForm):
    borrowing_equipment = SelectField(validators=[DataRequired()])
    user = SelectField(validators=[DataRequired()])
    name = StringField("Usage name", validators=[DataRequired(), Length(5, 2048)])
    usage_start_datetime = DateTimeField("Usage start date", validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    alt1_usage_planned_end_date = DateField("Planned usage end")
    #alt2_usage_duration_days = IntegerField("Planned usage duration in days")
    usage_location_id = SelectField(validators=[DataRequired()])
    submit = SubmitField("Borrow")
    
class BorrowMultipleEquipmentsForm(FlaskForm):
    borrowing_equipments = SelectMultipleField(coerce=int, validators=[Optional()])
    user = SelectField(validators=[DataRequired()])
    name = StringField("Usage name", validators=[DataRequired(), Length(5, 2048)])
    usage_start_datetime = DateTimeField("Usage start date", validators=[DataRequired()],format="%d.%m.%Y %H:%M:%S", default=get_current_time())
    alt1_usage_planned_end_date = DateField("Planned usage end")
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