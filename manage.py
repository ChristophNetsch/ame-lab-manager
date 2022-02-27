# -*- coding: utf-8 -*-
import dotenv
dotenv.load_dotenv()

from sqlalchemy.orm.mapper import configure_mappers

from ame_manager_app import create_app
from ame_manager_app.extensions import db
from ame_manager_app.user import Users, ADMIN, USER, ACTIVE
from ame_manager_app.tasks import MyTaskModel

application = create_app()


@application.cli.command("initdb")
def initdb():
    """Init/reset database."""

    db.drop_all()
    configure_mappers()
    db.create_all()

    admin = Users(name='Admin CVE AME Lab Manager',
                  name_short="CNH",
                  email=u'cnh@csem.ch',
                  password=u'adminpassword',
                  role_code=ADMIN,
                  status_code=ACTIVE)

    db.session.add(admin)

    for i in range(1, 2):
        user = Users(name='Micha Landoll',
                     name_short="MML",
                     email=u'landoll@ame.rwth-aachen',
                     password=u'demopassword',
                     role_code=USER,
                     status_code=ACTIVE)
        db.session.add(user)

    for i in range(1, 5):
        _usage = Users(usage="usage Random Number ## " + str(i), users_id=2)

        db.session.add(_usage)

    db.session.commit()

    print("Database initialized with 2 users (admin, demo)")
