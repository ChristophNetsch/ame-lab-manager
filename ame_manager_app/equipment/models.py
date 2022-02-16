# -*- coding: utf-8 -*-

from sqlalchemy import Column

from ..extensions import db
from ..utils import get_current_time

from flask_login import current_user
from flask_admin.contrib import sqla


class MyTaskModel(db.Model):

    __tablename__ = 'device'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_calibration_last = Column(db.DateTime, default=get_current_time)
    date_calibration_until = Column(db.DateTime, default=get_current_time)
    storage_location_id = Column(db.String(2048))
    info_text = Column(db.Text)
    reference_url = Column(db.String(2048))
    responsibleUserId = Column(db.String(2048))
    currentUsageId = (ForeignKey = Usage.id)

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
