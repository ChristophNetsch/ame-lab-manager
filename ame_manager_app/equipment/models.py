# -*- coding: utf-8 -*-

from sqlalchemy import Column

from ..extensions import db
from ..utils import get_current_time

from flask_login import current_user
from flask_admin.contrib import sqla


class EquipmentModel(db.Model):

    __tablename__ = 'equipment'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_calibration_last = Column(db.DateTime, default=get_current_time)
    date_calibration_until = Column(db.DateTime, default=get_current_time)
    storage_location_id = Column(db.Integer)
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.Integer)
    usages = db.relationship("UsageModel", backref="equipment")
    is_usable_bool = Column(db.Boolean)

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)


class CommentModel(db.Model):

    __tablename__ = 'comment'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    is_comment_for_responsible_admin = Column(db.Boolean)
    is_comment_for_users = Column(db.Boolean)

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)

class UsageModel(db.Model):

    __tablename__ = 'usage'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_start = Column(db.DateTime, default=get_current_time)
    date_planned_end = Column(db.DateTime, default=get_current_time)
    date_end = Column(db.DateTime, default=get_current_time)
    storage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id"))
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    reference_url = Column(db.String(2048))
    is_in_use_bool = Column(db.Boolean)
    #current_user_id = Column(db.Integer, db.ForeignKey("user.id"))

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)        

class StorageModel(db.Model):

    __tablename__ = 'storage_location'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    room_id = Column(db.Integer, db.ForeignKey("room.id"))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.String(2048))

    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)        

class RoomModel(db.Model):

    __tablename__ = 'room'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsible_user_id = Column(db.String(2048))
    
    def __unicode__(self):
        _str = 'ID: %s, Post: %s' % (self.id, self.task)
        return str(_str)        


# Customized MyTask model admin
class MyTaskModelAdmin(sqla.ModelView):
    column_sortable_list = ('id', 'users_id', 'added_time')

    column_filters = ('id', 'users_id', 'added_time')

    def __init__(self, session):
        super(MyTaskModelAdmin, self).__init__(MyTaskModel, session)

    def is_accessible(self):
        if current_user.role == 'admin':
            return current_user.is_authenticated()
