# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange

from ame_manager_app.config import DefaultConfig

class BorrowEquipmentForm(FlaskForm):
    name = TextAreaField("Usage Name", [InputRequired(), Length(5, 2048)])
    usage_duration_days = IntegerField("Usage Duration (days)", [InputRequired(), NumberRange(min=1, max=DefaultConfig.MAX_DAYS_BORROW)])
    usage_location_id = IntegerField("Usage Duration (days)", [InputRequired()])
    submit = SubmitField("Borrow")


class SearchEquipmentForm(FlaskForm):
    name = TextAreaField("Usage Name", [Length(5, 2048)])
    storage_location = TextAreaField("Storage Location", [Length(5, 2048)])
    room = TextAreaField("Room", [Length(5, 2048)])
    submit = SubmitField("Search")