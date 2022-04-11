# -*- coding: utf-8 -*-
from __future__ import annotations
from datetime import datetime

import random
from flask import flash, redirect, url_for

from flask_admin.contrib import sqla
from flask_login import current_user
from sqlalchemy import Column

from ame_manager_app.user.models import Users

from ..extensions import db
from ..utils import get_current_time, add_offset_days_on_datetime

class UsageModel(db.Model):

    __tablename__ = "usage"

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_start = Column(db.DateTime, default=get_current_time)
    date_planned_end = Column(db.DateTime)
    date_end = Column(db.DateTime)
    usage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id")) 
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    #reference_url = Column(db.String(2048)) # Wiki
    is_in_use = Column(db.Boolean)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"{self.name} (equipment:{self.equipment.name}, user:{self.user.name}, date_start:{self.date_start})"


class EquipmentModel(db.Model):

    __tablename__ = "equipment"

    id = Column(db.Integer, primary_key=True)
    id_lab_CVE= Column(db.Integer)
    id_lab_UKA= Column(db.Integer)
    name = Column(db.String(2048))
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))
    info_text = Column(db.Text)
    storage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id")) # original location not current
    reference_url = Column(db.String(2048)) # labmanager
    is_usable = Column(db.Boolean)
    is_calibration_nessessary = Column(db.Boolean)
    is_briefing_nessessary = Column(db.Boolean)

    calibrations = db.relationship(
        "CalibrationModel",
        backref=db.backref("equipment", lazy="joined"),
        lazy="select",
    )

    comments = db.relationship(  
        "CommentModel",     
        backref=db.backref("equipment", lazy="joined"),
        lazy="select",
    )
    usages = db.relationship(
        "UsageModel",
        backref=db.backref("equipment", lazy="joined"),
        lazy="select",
    )
    # Einweisungen
    briefings = db.relationship(
        "BriefingModel",
        backref=db.backref("equipment", lazy="joined"),
        lazy="select",
    )

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"{self.name} (id #{self.id}))"

    def is_in_use(self):
        return self.get_current_active_usage() is not None

    def is_in_use_by(self, user:Users):
        current_active_usage = self.get_current_active_usage()
        if current_active_usage is None:
            return False
        if not current_active_usage.user_id == user.id:
            return False
        return True
            
    def get_current_active_usage(self) -> UsageModel:
        usages = [
            u for u in sorted(self.usages, key=lambda x: x.date_start) if u.is_in_use
        ]
        if len(usages) > 0:
            if len(usages) > 1:
                print(f"Warning: multiple active usages registered for {self}.")
            return usages[-1]
        else:
            return None

    def return_equipment(self):
        current_active_usage = self.get_current_active_usage()
        print(current_active_usage)
        if current_active_usage is not None:
            current_active_usage.is_in_use = False
            current_active_usage.date_end = get_current_time()
            db.session.commit()
            
        else:
            raise Exception(
                f"Equipment {self} cannot be returned, since it has not been borrowed."
            )
            
    def borrow_equipment(self,name,usage_start,usage_planned_end,borrowing_user_id,usage_location_id):
        if not self.is_in_use():
            _usage = UsageModel(
                user_id=borrowing_user_id,
                name=name,
                date_start = usage_start,
                #date_planned_end=add_offset_days_on_datetime(get_current_time(), usage_duration_days),
                date_planned_end=usage_planned_end,
                usage_location_id = usage_location_id,
                equipment_id=self.id,
                is_in_use=True,
            )
            db.session.add(_usage)
            db.session.commit()
            flash(f'Borrowing Equipment successfull.', 'success')
            
        else:
            raise Exception(
                f"Equipment {self} cannot be borrowed, already in use with usage {self.get_current_active_usage()}."
            )
    def add_briefing(self,date,text,user_id,date_until,briefer_id):
        if date_until is None:
            _briefing = BriefingModel(
                user_id=user_id,
                briefer_id=briefer_id,
                date = date,
                equipment_id=self.id,
                text = text,
            )
        else:
            _briefing = BriefingModel(
                user_id=user_id,
                briefer_id=briefer_id,
                date = date,
                equipment_id=self.id,
                text = text,
                date_until=date_until,
                )
        db.session.add(_briefing)
        db.session.commit()
        flash(f'Briefing submission successfull.', 'success')

    def add_comment(self,date,text,user_id, is_comment_for_responsible_admin, is_comment_for_users):
        _comment = CommentModel(
            user_id=user_id,
            date = date,
            equipment_id=self.id,
            text = text,
            is_comment_for_responsible_admin = is_comment_for_responsible_admin,
            is_comment_for_users = is_comment_for_users,
        )
        db.session.add(_comment)
        db.session.commit()
        flash(f'Comment submission successfull.', 'success')
        
    def add_calibration(self,date,text,user_id,date_until):
        _comment = CalibrationModel(
            user_id=user_id,
            date = date,
            equipment_id=self.id,
            text = text,
            date_until = date_until,
        )
        db.session.add(_comment)
        db.session.commit()
        flash(f'Calibration submission successfull.', 'success')

class CommentModel(db.Model):

    __tablename__ = "comment"

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    is_comment_for_responsible_admin = Column(db.Boolean, default=False)
    is_comment_for_users = Column(db.Boolean, default=True)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"{self.text} (id #{self.id}, user:{self.user.name}, date:{self.date}))"

class CalibrationModel(db.Model):

    __tablename__ = "calibration"

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    date_until= Column(db.Date)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"{self.text} (id #{self.id}, user:{self.user.name}, date:{self.date}))"

class BriefingModel(db.Model):

    __tablename__ = "briefing"

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    briefer_id= Column(db.Integer, db.ForeignKey("user.id"))
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    date_until= Column(db.Date)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"user:{self.user_id}, id #{self.equipment_id}, date:{self.date}"

class StorageModel(db.Model):

    __tablename__ = "storage_location"

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    room_id = Column(db.Integer, db.ForeignKey("room.id"))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))

    stored_equipment = db.relationship(
        "EquipmentModel",
        backref=db.backref("storage_location", lazy="joined"),
        lazy="select",
    )

    usages = db.relationship(
        "UsageModel",
        backref=db.backref("usage_location", lazy="joined"),
        lazy="select",
    )

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return f"{self.name} - {self.room.name}"

class RoomModel(db.Model):

    __tablename__ = "room"

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))

    storage_locations = db.relationship(
        "StorageModel",
        backref=db.backref("room", lazy="joined"),
        lazy="select",
    )

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return self.name


# Customized UsageModelAdmin model admin
class UsageModelAdmin(sqla.ModelView):
    form_excluded_columns = ("is_in_use", "date_end")
    
    def __init__(self, session):
        super(UsageModelAdmin, self).__init__(UsageModel, session)

    def is_accessible(self):
        if current_user.role == "admin":
            return current_user.is_authenticated()
