# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import Column

from ame_manager_app.user.models import Users

from ..extensions import db
from ..utils import get_current_time, get_current_time_with_offset_days

from flask_login import current_user
from flask_admin.contrib import sqla


class EquipmentModel(db.Model):

    __tablename__ = 'equipment'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_calibration_last = Column(db.DateTime)
    date_calibration_until = Column(db.DateTime)
    storage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id"))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    is_usable = Column(db.Boolean)
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))

    responsible_rooms = db.relationship("CommentModel", 
                                        backref=db.backref("equipment", lazy="joined"),
                                        lazy="select",
                                        )
    usages = db.relationship("UsageModel", 
                            backref=db.backref("equipment", lazy="joined"),
                            lazy="select",
                            )

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"

    def is_in_use(self):
        return self.get_current_active_usage() is not None

    def get_current_active_usage(self):
        usages = [u for u in sorted(self.usages, key=lambda x: x.date_start) if u.is_in_use]
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
            raise Exception(f"Equipment {self} cannot be returned, since it has not been borrowed.")

    def borrow_equipment(self, user:Users, 
                         usage_location: "StorageModel", 
                         name:str="", 
                         usage_duration_days:int=90):
        if not self.is_in_use():
            _usage = UsageModel(name=name,
                                date_start=get_current_time(),
                                date_planned_end=get_current_time_with_offset_days(usage_duration_days),
                                usage_location=usage_location,
                                equipment=self,
                                is_in_use=True,
                                user=user,
                                )
            db.session.add(_usage)
            db.session.commit()
        else:
            raise Exception(f"Equipment {self} cannot be borrowed, already in use with usage {self.get_current_active_usage()}.")

class CommentModel(db.Model):

    __tablename__ = 'comment'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    is_comment_for_responsible_admin = Column(db.Boolean, default=False)
    is_comment_for_users = Column(db.Boolean, default=True)

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.text}, date={self.date}, user={self.user.name}, is_comment_for_responsible_admin={self.is_comment_for_responsible_admin}, is_comment_for_users={self.is_comment_for_users})"
    
class UsageModel(db.Model):

    __tablename__ = 'usage'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_start = Column(db.DateTime, default=get_current_time)
    date_planned_end = Column(db.DateTime)
    date_end = Column(db.DateTime)
    usage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id"))
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    reference_url = Column(db.String(2048))
    is_in_use = Column(db.Boolean)

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, equipment={self.equipment.name}, user={self.user.name}, date_start={self.date_start})"

class StorageModel(db.Model):

    __tablename__ = 'storage_location'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    room_id = Column(db.Integer, db.ForeignKey("room.id"))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))

    stored_equipment = db.relationship("EquipmentModel", 
                                backref=db.backref("storage_location", lazy="joined"),
                                lazy="select",
                                )

    usages = db.relationship("UsageModel", 
                            backref=db.backref("usage_location", lazy="joined"),
                            lazy="select",
                            )

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)        

class RoomModel(db.Model):

    __tablename__ = 'room'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.Integer, db.ForeignKey("user.id"))
    
    storage_locations = db.relationship("StorageModel", 
                                        backref=db.backref("room", lazy="joined"),
                                        lazy="select",
                                        )
    
    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)        


# Customized UsageModelAdmin model admin
class UsageModelAdmin(sqla.ModelView):
    column_sortable_list = ('id', 'user_id', 'added_time')

    column_filters = ('id', 'user_id', 'added_time')

    def __init__(self, session):
        super(UsageModelAdmin, self).__init__(UsageModel, session)

    def is_accessible(self):
        if current_user.role == 'admin':
            return current_user.is_authenticated()
