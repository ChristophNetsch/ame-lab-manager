# -*- coding: utf-8 -*-
import os
import random

import dotenv

from ame_manager_app.utils import get_current_time_with_offset_days

dotenv.load_dotenv()

from sqlalchemy.orm.mapper import configure_mappers

from ame_manager_app import create_app
from ame_manager_app.equipment.models import (BriefingModel, CalibrationModel, CommentModel, EquipmentModel, KickerMatchModel, LocationUsageModel,
                                              RoomModel, StorageModel,
                                              UsageModel)
from ame_manager_app.extensions import db
from ame_manager_app.user import ACTIVE, ADMIN, USER, Users

application = create_app()

@application.cli.command("initdb")
def initdb():
    db.drop_all()
    configure_mappers()
    db.create_all()
    
    admin = Users(
        name="admin",
        name_short="adm",
        email=os.getenv("ADMIN_EMAIL"),
        password=os.getenv("ADMIN_DEFAULT_PASSWORD"),
        role_code=ADMIN,
        status_code=ACTIVE,
    )
    
    db.session.add(admin)
    db.session.commit()
    
@application.cli.command("inittestdb")
def inittestdb():
    """Init/reset database and write some dummy data to each table."""

    db.drop_all()
    configure_mappers()
    db.create_all()

    admin = Users(
        name="Rick",
        name_short="rck",
        email="rck@ame.rwth-aachen.de",
        password="adminpassword",
        role_code=ADMIN,
        status_code=ACTIVE,
    )

    user = Users(
        name="Morty",
        name_short="mty",
        email="mty@ame.rwth-aachen.de",
        password="demopassword",
        role_code=USER,
        status_code=ACTIVE,
    )

    _room = RoomModel(
        name="secret lab",
        info_text="deep in the AME cellars",
        reference_url="",
        responsible_user=admin,
    )
    db.session.add(_room)
    _room = RoomModel.query.filter_by(name=_room.name).first()
    
    _storage1 = StorageModel(
        name="box 1",
        room=_room,
        info_text="impossible to find",
        responsible_user=admin,
    )
    db.session.add(_storage1)

    _storage2 = StorageModel(
        name="refrigerator",
        room=_room,
        info_text="No snacks! Only for embryos!",
        responsible_user=user,
    )

    _equipments = []
    for equipment_name in [
        "portal gun",
        "ionic defibuilzer",
        "plumbus",
        "inter-dimensional goggles",
        "microverse battery",
    ]:
        _equipment = EquipmentModel(
            name=equipment_name,            
            is_briefing_nessessary = random.choice([True, False]),
            is_calibration_nessessary=random.choice([True, False]),
            storage_location=random.choice([_storage1, _storage2]),
            is_usable=random.choice([True, False]),
            responsible_user=admin,
            id_lab_UKA=random.randint(10000,99999),
            id_lab_CVE=random.randint(0,1000),
            datetime_register = get_current_time_with_offset_days(random.randint(-365, -1))
        )

        db.session.add(_equipment)
        _equipments.append(_equipment)

    for comment_text in ["best equipment ever", "Does it work?", "Do not touch!"]:
        _comment = CommentModel(
            text=comment_text,
            user=random.choice([admin, user]),
            equipment=random.choice(_equipments),
            is_comment_for_responsible_admin=random.choice([True, False]),
            is_comment_for_users=random.choice([True, False]),
        )
        db.session.add(_comment)

    for calibration_text in ["calibration for next two weeks", "device calibrated"]:
        _calibration = CalibrationModel(
            user=random.choice([admin, user]),
            equipment=random.choice(_equipments),
            text=calibration_text,
            date_until=get_current_time_with_offset_days(random.randint(1, 365)),
        )
        db.session.add(_calibration)

    for briefing_text in ["User is now briefed", "devices for dummys!"]:
        _briefing= BriefingModel(
            user=user,
            briefer=admin,
            equipment=random.choice(_equipments),
            text=briefing_text,
            date=get_current_time_with_offset_days(random.randint(-10,-1)),
            date_until=get_current_time_with_offset_days(random.randint(365,365*3)),
        )
        db.session.add(_briefing)
        
    _usages = []
    for _equipment in _equipments:
        print(f"Borrowing {_equipment}")
        _usage = UsageModel(
            name="secret experiment",
            date_start=get_current_time_with_offset_days(random.randint(-365, -1)),
            date_planned_end=get_current_time_with_offset_days(random.randint(1, 365)),
            usage_location=random.choice([_storage1, _storage2]),
            equipment=_equipment,
            is_in_use=True,
            user=random.choice([admin, user]),
        )

        db.session.add(_usage)
        _usages.append(_usage)

    db.session.commit()

    _used_equipments = EquipmentModel.query.filter(
        EquipmentModel.usages.any(UsageModel.is_in_use == True)
    ).all()

    _return_equipments = _used_equipments[:2]
    for _return_equipment in _return_equipments:
        print(f"Returning {_return_equipment}")
        _return_equipment.return_equipment()

    _unused_equipments = EquipmentModel.query.filter(
        EquipmentModel.usages.any(is_in_use=False)
    ).all()
    for _unused_equipment in _unused_equipments:
        print(f"Borrowing {_unused_equipment}")
        _unused_equipment.borrow_equipment(
            borrowing_user=random.choice([admin, user]),
            usage_location=random.choice([_storage1, _storage2]),
            name="secret experiment round 2",
            usage_start = get_current_time_with_offset_days(random.randint(-365, -1)),
            usage_planned_end = get_current_time_with_offset_days(random.randint(1, 365)),
        )

    _location_usages = []
    for _storage in [_storage1, _storage2]:
        print(f"Borrowing location {_storage}")
        _location_usage = LocationUsageModel(
            name="secret experiment",
            date_start=get_current_time_with_offset_days(random.randint(-365, -1)),
            date_planned_end=get_current_time_with_offset_days(random.randint(1, 365)),
            location_usage=_storage,
            is_in_use=True,
            user=random.choice([admin, user]),
        )

        db.session.add(_location_usage)
        _location_usages.append(_location_usage)

    db.session.commit()

    _used_locations = StorageModel.query.filter(
        StorageModel.location_usages.any(LocationUsageModel.is_in_use == True)
    ).all()

    _return_locations = _used_locations[:2]
    for _return_location in _return_locations:
        print(f"Returning location usage {_return_location}")
        _return_location.return_location_usage()
    
    #add kicker match
    _goals_team1 = random.randint(0,10)
    _goals_team2 = random.randint(0,10)
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
        team_1_player1=random.choice([user, admin]),
        team_1_player2=random.choice([user, admin]),
        team_2_player1=random.choice([user, admin]),
        team_2_player2=random.choice([user, admin]),
        goals_team1 = _goals_team1,
        goals_team2 = _goals_team2,
        date = get_current_time_with_offset_days(random.randint(-365, -1)),
        is_crawl = _is_crawl,
        is_team1_winner = _is_team1_winner,
        is_team2_winner = _is_team2_winner,
    )
    db.session.add(_match)
    db.session.commit()
    print("Kicker Match succesfuly initialized with dummy data.")
