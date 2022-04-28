# -*- coding: utf-8 -*-
import random
import logging
import dotenv
from pathlib2 import Path

from ame_manager_app.utils import get_current_time_with_offset_days

dotenv.load_dotenv()

from sqlalchemy.orm.mapper import configure_mappers

from ame_manager_app import create_app
from ame_manager_app.equipment.models import (BriefingModel, CalibrationModel, CommentModel, EquipmentModel,
                                              RoomModel, StorageModel,
                                              UsageModel)
from ame_manager_app.extensions import db
from ame_manager_app.user import ACTIVE, ADMIN, USER, Users

application = create_app()


@application.cli.command("initdb")
def initdb_if_not_exists():
    if not Path(application.config["SQLITE_DATABASE_PATH"]).exists():
        db.create_all()
        # Create admin user
        admin = Users(
            name="admin",
            name_short="admin",
            email="micha.landoll@rwth-aachen.de",
            password="adminpassword",
            role_code=ADMIN,
            status_code=ACTIVE,
        )
        db.session.add(admin)
        db.session.commit()
        print("Created new database with user admin/adminpassword")
        return
    print("Database already exists")
    return

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

    print("Database successfully initialized with dummy data.")


if __name__ == '__main__':
    initdb_if_not_exists()
    application.run()