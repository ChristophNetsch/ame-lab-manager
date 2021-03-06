# -*- coding: utf-8 -*-
from __future__ import annotations


from flask_admin.contrib import sqla
from flask_login import current_user
from sqlalchemy import Column
from ame_manager_app.user.models import Users

from ..extensions import db
from ..utils import get_current_time

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
        return f"name: {self.name} (equipment: {self.equipment.name}, user: {self.user}, date_start: {self.date_start})"

class LocationUsageModel(db.Model):

    __tablename__ = "location_usage"

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(2048))
    date_start = Column(db.DateTime, default=get_current_time)
    date_planned_end = Column(db.DateTime)
    date_end = Column(db.DateTime)
    usage_location_id = Column(db.Integer, db.ForeignKey("storage_location.id")) 
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    #reference_url = Column(db.String(2048)) # Wiki
    is_in_use = Column(db.Boolean)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"name: {self.name} (location: {self.location_usage.name}, user: {self.user}, date_start: {self.date_start})"


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
    datetime_register = Column(db.DateTime, default=get_current_time)

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

    def get_resp_user(self) -> Users:
        user = Users.query.filter_by(id=self.responsible_user_id).first()
        return user
    
    def get_storage_location(self) -> StorageModel:
        storage = StorageModel.query.filter_by(id=self.storage_location_id).first()
        return storage

    def get_latest_location(self) -> StorageModel:
        storage = StorageModel.query.filter_by(id=self.storage_location_id).first()
        if self.is_in_use() ==True:
            storage = StorageModel.query.filter_by(id=self.get_current_active_usage().usage_location_id).first()
        return storage

    def return_equipment(self):
        current_active_usage = self.get_current_active_usage()
        if current_active_usage is not None:
            current_active_usage.is_in_use = False
            current_active_usage.date_end = get_current_time()
            db.session.commit()
        else:
            raise Exception(
                f"Equipment {self} cannot be returned, since it has not been borrowed."
            )
            
    def borrow_equipment(self,name,usage_start,usage_planned_end,borrowing_user,usage_location):
        if not self.is_in_use():
            _usage = UsageModel(
                user_id=borrowing_user.id,
                name=name,
                date_start = usage_start,
                #date_planned_end=add_offset_days_on_datetime(get_current_time(), usage_duration_days),
                date_planned_end=usage_planned_end,
                usage_location_id = usage_location.id,
                equipment_id=self.id,
                is_in_use=True,
            )
            db.session.add(_usage)
            db.session.commit()            
        else:
            raise Exception(
                f"Equipment {self} cannot be borrowed, already in use with usage {self.get_current_active_usage()}."
            )
    def add_briefing(self,date,text,user,date_until,briefer):
        if date_until is None:
            _briefing = BriefingModel(
                user_id=user.id,
                briefer_id=briefer.id,
                date = date,
                equipment_id=self.id,
                text = text,
            )
        else:
            _briefing = BriefingModel(
                user_id=user.id,
                briefer_id=briefer.id,
                date = date,
                equipment_id=self.id,
                text = text,
                date_until=date_until,
                )
        db.session.add(_briefing)
        db.session.commit()

    def add_comment(self,date,text,user, is_comment_for_responsible_admin, is_comment_for_users):
        _comment = CommentModel(
            user_id=user.id,
            date = date,
            equipment_id=self.id,
            text = text,
            is_comment_for_responsible_admin = is_comment_for_responsible_admin,
            is_comment_for_users = is_comment_for_users,
        )
        db.session.add(_comment)
        db.session.commit()
        
    def add_calibration(self,date,text,user,date_until):
        _comment = CalibrationModel(
            user_id=user.id,
            date = date,
            equipment_id=self.id,
            text = text,
            date_until = date_until,
        )
        db.session.add(_comment)
        db.session.commit()
        
    def register_equipment(
        storage_location,
        responsible_user,
        name:str="",
        info_text:str="",
        reference_url:str="",
        id_lab_UKA:str="",
        id_lab_CVE:str="",
        is_usable:bool=False,
        is_calibration_nessessary:bool=False,
        is_briefing_nessessary:bool=False,
        ):
        _equipment = EquipmentModel(
            responsible_user_id=responsible_user.id,
            name=name,
            info_text=info_text,
            reference_url=reference_url,
            storage_location_id=storage_location.id,
            id_lab_UKA=id_lab_UKA,
            id_lab_CVE=id_lab_CVE,
            is_usable=is_usable,
            is_calibration_nessessary=is_calibration_nessessary,
            is_briefing_nessessary=is_briefing_nessessary,
            datetime_register=get_current_time(),
        )
        db.session.add(_equipment)
        db.session.commit()
        
    def add_kicker_match(self,
        _team_1_player_1,
        _team_1_player_2,
        _team_2_player_1,
        _team_2_player_2,
        _goals_team1,
        _goals_team2,
    ):
        _is_team1_winner = False
        _is_team2_winner = False
        if _goals_team1>_goals_team2:
            _is_team1_winner = True
        elif _goals_team1<_goals_team2:
            _is_team2_winner = True
            
        _is_crawl = False
        if _goals_team1<=0 or _goals_team2<=0:
            _is_crawl = True
            
        _match = KickerMatchModel(
            team_1_player1=_team_1_player_1,
            team_1_player2=_team_1_player_2,
            team_2_player1=_team_2_player_1,
            team_2_player2=_team_2_player_2,
            goals_team1 = _goals_team1,
            goals_team2 = _goals_team2,
            date = get_current_time(),
            is_crawl = _is_crawl,
            is_team1_winner = _is_team1_winner,
            is_team2_winner = _is_team2_winner,
        )
        db.session.add(_match)
        db.session.commit()
    
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
        return f"{self.text} (id #{self.id}, user:{self.user_id}, date:{self.date}))"

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
        return f"{self.text} (equipment:{self.equipment_id}, user:{self.user_id}, date:{self.date}))"

class BriefingModel(db.Model):

    __tablename__ = "briefing"

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("user.id"))
    briefer_id= Column(db.Integer, db.ForeignKey("user.id"))
    
    user = db.relationship("Users", foreign_keys=[user_id])
    briefer = db.relationship("Users", foreign_keys=[briefer_id])
    
    date = Column(db.DateTime, default=get_current_time)
    equipment_id = Column(db.Integer, db.ForeignKey("equipment.id"))
    text = Column(db.Text)
    date_until= Column(db.Date)

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)

    def __repr__(self):
        return f"user:{self.user_id}, id #{self.equipment_id}, date:{self.date}"
    
    def get_user(self) -> Users:
        user = Users.query.filter_by(id=self.user_id).first()
        return user
    
    def get_briefer(self) -> Users:
        briefer = Users.query.filter_by(id=self.briefer_id).first()
        return briefer

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
    location_usages = db.relationship(
        "LocationUsageModel",
        backref=db.backref("location_usage", lazy="joined"),
        lazy="select",
    )
    def is_in_use(self):
        return self.get_current_active_usage() is not None

    def is_in_use_by(self, user:Users):
        current_active_usage = self.get_current_active_usage()
        if current_active_usage is None:
            return False
        if not current_active_usage.user_id == user.id:
            return False
        return True
            
    def get_current_active_usage(self) -> LocationUsageModel:
        usages = [
            u for u in sorted(self.location_usages, key=lambda x: x.date_start) if u.is_in_use
        ]
        if len(usages) > 0:
            if len(usages) > 1:
                print(f"Warning: multiple active usages registered for {self}.")
            return usages[-1]
        else:
            return None

    def return_location_usage(self):
        current_active_usage = self.get_current_active_usage()
        if current_active_usage is not None:
            current_active_usage.is_in_use = False
            current_active_usage.date_end = get_current_time()
            db.session.commit()
        else:
            raise Exception(
                f"Equipment {self} cannot be returned, since it has not been borrowed."
            )
            
    def borrow_location_usage(self,name,usage_start,usage_planned_end,borrowing_user):
        if not self.is_in_use():
            _usage = LocationUsageModel(
                user_id=borrowing_user.id,
                name=name,
                date_start = usage_start,
                #date_planned_end=add_offset_days_on_datetime(get_current_time(), usage_duration_days),
                date_planned_end=usage_planned_end,
                usage_location_id = self.id,
                is_in_use=True,
            )
            db.session.add(_usage)
            db.session.commit()            
        else:
            raise Exception(
                f"Location {self} cannot be borrowed, already in use with usage {self.get_current_active_usage()}."
            )
    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.task)
        return str(_str)
    
    def __repr__(self):
        return f"{self.name} in {self.room.name}"
    
    def get_resp_user(self) -> Users:
        user = Users.query.filter_by(id=self.responsible_user_id).first()
        return user

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
        _str = "ID: %s, Post: %s" % (self.id, self.name)
        return str(_str)
    
    def __repr__(self):
        return self.name
    
    def get_resp_user(self) -> Users:
        user = Users.query.filter_by(id=self.responsible_user_id).first()
        return user

# Customized UsageModelAdmin model admin
class UsageModelAdmin(sqla.ModelView):
    form_excluded_columns = ("is_in_use", "date_end")
    
    def __init__(self, session):
        super(UsageModelAdmin, self).__init__(UsageModel, session)

    def is_accessible(self):
        if current_user.role == "admin":
            return current_user.is_authenticated()

class KickerMatchModel(db.Model):

    __tablename__ = "kicker_match"

    id = Column(db.Integer, primary_key=True)
    date = Column(db.DateTime, default=get_current_time)
    goals_team1 = Column(db.Integer)
    goals_team2 = Column(db.Integer)
    is_team1_winner = Column(db.Boolean)
    is_team2_winner = Column(db.Boolean)
    is_crawl = Column(db.Boolean)

    team_1_player1_id = Column(db.Integer, db.ForeignKey("user.id"))
    team_1_player2_id = Column(db.Integer, db.ForeignKey("user.id"))
    team_2_player1_id = Column(db.Integer, db.ForeignKey("user.id"))
    team_2_player2_id = Column(db.Integer, db.ForeignKey("user.id"))
    team_1_player1 = db.relationship("Users",foreign_keys=[team_1_player1_id])
    team_1_player2 = db.relationship("Users",foreign_keys=[team_1_player2_id])
    team_2_player1 = db.relationship("Users",foreign_keys=[team_2_player1_id])
    team_2_player2 = db.relationship("Users",foreign_keys=[team_2_player2_id])

    def __unicode__(self):
        _str = "ID: %s, Post: %s" % (self.id, self.date)
        return str(_str)
    
    def __repr__(self):
        return f"Team 1:{self.team_1_player1.name_short}+{self.team_1_player2.name_short}, {self.goals_team1}:{self.goals_team2}, Team 2:{self.team_2_player1.name_short},{self.team_2_player2.name_short}, date:{self.date}"
