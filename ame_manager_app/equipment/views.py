# -*- coding: utf-8 -*-

import pathlib
from flask import Blueprint, current_app, flash, redirect, render_template, send_file, url_for
from ..utils import get_current_time
from flask_login import current_user, login_required
from ame_manager_app.equipment.forms import BorrowLocationForm, BorrowMultipleEquipmentsForm, RegisterEquipmentForm, FilterEquipmentForm,SearchEquipmentForm,BorrowEquipmentForm,AddCalibrationForm, AddBriefingForm, AddCommentForm, KickerMatchForm

from ame_manager_app.equipment.models import EquipmentModel, KickerMatchModel, StorageModel, UsageModel, LocationUsageModel, RoomModel
from ame_manager_app.user import ADMIN
from ame_manager_app.user.models import Users
import datetime
import qrcode
import io
from PIL import ImageFont, ImageDraw, Image

from ..extensions import db

equipment = Blueprint("equipment", __name__, url_prefix="/equipment")

@equipment.route("/register", methods=["GET", "POST"])
@login_required
def add_register_new_equipment():
    form = RegisterEquipmentForm()
    form.responsible_user.choices = [(user.id, user.name) for user in Users.query.filter(Users.role_code == ADMIN).all()]
    if current_user.role_code == ADMIN:
        form.responsible_user.default = current_user.id
    form.storage_location_id.choices = [(storage.id, str(storage.name) + " in " + str(storage.room_id)) for storage in StorageModel.query.all()]
    form.is_usable.data = True
    form.is_calibration_nessessary.data = False
    form.is_briefing_nessessary.data = False
    if form.validate_on_submit():
        _responsible_user=Users.query.filter_by(id=form.responsible_user.data).first()
        _storage_location=StorageModel.query.filter_by(id=form.storage_location_id.data).first()
        equipment_model = EquipmentModel(
            name=form.name.data,
            info_text=form.info_text.data,
            reference_url=form.reference_url.data,
            responsible_user_id=_responsible_user.id,
            storage_location_id=_storage_location.id,
            is_usable=form.is_usable.data,
            is_calibration_nessessary=form.is_calibration_nessessary.data,
            is_briefing_nessessary=form.is_briefing_nessessary.data,
            id_lab_CVE=form.id_lab_CVE.data,
            id_lab_UKA=form.id_lab_UKA.data
        )
        db.session.add(equipment_model)
        db.session.commit()
        flash("Equipment was registered", "success")
        return redirect(url_for('equipment.view_equipment', id=equipment_model.id))

    return render_template("equipment/register_equipment.html", form=form)

@equipment.route("/all_storages")
@login_required
def view_all_storages():
    storages = StorageModel.query.all()
    return render_template("equipment/all_storages.html", storages=storages)

@equipment.route("/all_rooms")
@login_required
def view_all_rooms():
    rooms = RoomModel.query.all()
    return render_template("equipment/all_rooms.html", rooms=rooms)

@equipment.route("/all_equipments")
@login_required
def view_all():
    equipments = EquipmentModel.query.all()
    return render_template("equipment/all_equipments.html", equipments=equipments)

@equipment.route("/search_page")
@login_required
def search():
    equipments = EquipmentModel.query.all()
    rooms = RoomModel.query.all()
    storages = StorageModel.query.all()
    _usages = UsageModel.query.filter_by(user_id=current_user.id).all()
    _location_usages = LocationUsageModel.query.filter_by(user_id=current_user.id).all()

    _form_search = SearchEquipmentForm()
    _form_search.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]

    _form_filter = FilterEquipmentForm()
    _form_filter.room.choices = [(room.id, room.name) for room in rooms]
    _form_filter.storage_location.choices = [(storage.id, storage.name) for storage in storages]
    _form_filter.usage_location.choices = [(storage.id, storage.name) for storage in storages]
    _form_filter.filter_mode.choices = ["Room ", "Storage location ", "Usage location "]
    
    if _form_filter.validate_on_submit():
        mode = _form_filter.filter_mode.data
        if mode== "Room ":
            _room = RoomModel.query.filter_by(id=_form_filter.room.data).first() 
            _storage_locations = _room.query.storage_locations.all()
            equipments = EquipmentModel.query.filter(EquipmentModel.storage_location_id in _storage_locations).all()
            _form_search.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
        if mode== "Storage location ":
            _storage_location =StorageModel.query.filter_by(id=_form_filter.storage_location.data).first() 
            equipments = EquipmentModel.query.filter(EquipmentModel.storage_location_id in _storage_locations).all()
            _form_search.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
        if mode== "Usage location ":
            _usage_location =StorageModel.query.filter_by(id=_form_filter.usage_location.data).first() 
            equipments = EquipmentModel.query.filter(EquipmentModel.get_current_active_usage().usage_location_id in _usage_location).all()
            
            _form_search.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
        if _form_search.validate_on_submit():
            _equipment = EquipmentModel.query.filter_by(id=_form_search.equipment_id.data).first()
            _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
            #return redirect(url_for('equipment.view_equipment', id=_equipment.id))
            
    return render_template(
        "equipment/search_equipment.html", 
        form_filter=_form_filter, 
        form_search = _form_search, 
        equipments = equipments,
        usages = _usages,
        user = current_user,
        _active_dash=True,
    )

@equipment.route('/my_page', methods=['GET', 'POST'])
@login_required
def my_page():
    _usages = UsageModel.query.filter_by(user_id=current_user.id).all()
    _location_usages = LocationUsageModel.query.filter_by(user_id=current_user.id).all()
    _responsible_equipments = EquipmentModel.query.filter_by(responsible_user_id=current_user.id).all()
    _responsible_storages = StorageModel.query.filter_by(responsible_user_id=current_user.id).all()
    _responsible_rooms = RoomModel.query.filter_by(responsible_user_id=current_user.id).all()

    return render_template('equipment/my_page.html',
                           user = current_user,
                           responsible_equipments=_responsible_equipments,
                           usages=_usages,
                           storages = _responsible_storages,
                           location_usages = _location_usages,
                           rooms = _responsible_rooms,
                           )

@equipment.route('/view_equipment/<id>', methods=['GET', 'POST'])
def view_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
    return render_template('equipment/equipment_page.html',
                           equipment=_equipment,
                           resp_user = _resp_user,
                           )
    
@equipment.route('/qr/<id>', methods=['GET', 'POST'])
def generate_qr(id):
    _equipment = EquipmentModel.query.filter_by(id=id).first()
    file = qrcode.make(url_for('equipment.view_equipment', id=_equipment.id))
    buf = io.BytesIO()
    file.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')
 
@equipment.route('/view_room/<id>', methods=['GET', 'POST'])
def view_room(id):
    _room = RoomModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _room.responsible_user_id).first()
    _storages = StorageModel.query.filter_by(room_id=id).all()
    _all_equipment_from_storages=[]
    _in_use_equipment_from_storages=[]
    _usable_equipment_from_storages=[]
    for _storage in _storages:
        _all_equipment_from_storages.append(EquipmentModel.query.filter(EquipmentModel.storage_location_id == _storage.id).all())
    return render_template('equipment/room_page.html',
                           room=_room,
                           resp_user=_resp_user,
                           storages = _storages,
                           all_equipment = _all_equipment_from_storages,
                           )


@equipment.route('/view_storage/<id>', methods=['GET', 'POST'])
def view_storage(id):
    _storage = StorageModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _storage.responsible_user_id).first()
    _location_usages = LocationUsageModel.query.filter_by(usage_location_id=id).all()
    return render_template('equipment/storage_page.html',
                            storage=_storage,
                            resp_user = _resp_user,
                            location_usages = _location_usages,
                           )

@equipment.route('/borrow_location/<id>', methods=['GET', 'POST'])
@login_required
def borrow_location(id):
    _location:StorageModel = StorageModel.query.filter_by(id=id).first()
    storages = StorageModel.query.filter_by(room_id=1).all()
    equipments = EquipmentModel.query.filter_by(is_usable=True).all()
    is_not_in_use_locations=[]
    for location in storages:
        if location.is_in_use()==False:
            is_not_in_use_locations.append(location)
    users = Users.query.all()
    storages_names = [(storage.name) for storage in storages]
    _form = BorrowLocationForm()
    _form.borrowing_location.choices = [(storage.id, storage.name) for storage in storages]
    _form.borrowing_location.default = _location.id
    _form.alt1_usage_planned_end_date.data = datetime.date.today() + datetime.timedelta(days=1)
    #_form.alt2_usage_duration_days.data = int(1)
    _form.name.data = "experimentname"
    _form.user.choices = [(user.id, user.name) for user in users]
        
    if _location is None:
        flash(f'Location {_location.name} with id {id} does not exist!', 'danger')
        return redirect("/equipment/my_page")
    
    if _location.is_in_use():
        flash(f'Location {_location.name} with id {id} is currently in use by {_location.get_current_active_usage().user}!', 'danger')
        return redirect("/equipment/my_page") #return redirect(url_for('equipment.view_equipment', id=_equipment.id))
    
    if _form.validate_on_submit():
        _location=StorageModel.query.filter_by(id=_form.borrowing_location.data).first()
        _user=Users.query.filter_by(id=_form.user.data).first()
        _location.borrow_location_usage(
            name=_form.name.data,
            usage_start= _form.usage_start_datetime.data,
            usage_planned_end= _form.alt1_usage_planned_end_date.data,
            #usage_duration_days= _form.alt2_usage_duration_days.data,
            borrowing_user=_user,
            )
        flash(f'Borrowing Location successful.', 'success')

    flash(f'You can borrow this location. Please add some spicy infos.', 'secondary')
    return render_template('equipment/borrow_location.html', form=_form, location=_location)

@equipment.route('/return_location/<id>', methods=['GET', 'POST'])
@login_required
def return_location(id):
    _location:StorageModel = StorageModel.query.filter_by(id=id).first()
    
    if _location is None:
        flash(f'Location {_location.name} with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    if _location.is_in_use() ==False:
        flash(f"Location {_location.name} with id {id} cannot be returned, since it has not been borrowed.", 'danger')
        return redirect(url_for("equipment.my_page"))
            
    if not _location.is_in_use_by(current_user) and not current_user.role_code==ADMIN:
        flash(f'Location {_location.name} with id {id} has not been borrowed by you.', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    _location.return_location_usage()
    flash(f'Location {_location.name} has been returned succesfuly.', 'success')
    return redirect(url_for("equipment.my_page"))
    

@equipment.route('/borrow/<id>', methods=['GET', 'POST'])
@login_required
def borrow_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    storages = StorageModel.query.filter_by(room_id=1).all()
    equipments = EquipmentModel.query.filter_by(is_usable=True).all()
    is_not_in_use_equipments=[]
    for equipment in equipments:
        if equipment.is_in_use()==False:
            is_not_in_use_equipments.append(equipment)
    users = Users.query.all()
    storages_names = [(storage.name) for storage in storages]
    _form = BorrowEquipmentForm()
    _form.usage_location_id.choices = [(storage.id, storage.name) for storage in storages]
    _form.alt1_usage_planned_end_date.data = datetime.date.today() + datetime.timedelta(days=1)
    #_form.alt2_usage_duration_days.data = int(1)
    _form.name.data = "experimentname"
    _form.user.choices = [(user.id, user.name) for user in users]
    _form.borrowing_equipment.choices = [(equipment.id, equipment.name) for equipment in is_not_in_use_equipments]
    _form.borrowing_equipment.default = _equipment.id #(_equipment.id, _equipment.name)
        
    if _equipment is None:
        flash(f'Equipment {_equipment.name} with id {id} does not exist!', 'danger')
        return redirect(url_for('equipment.register_equipment'))
    
    if _equipment.is_in_use():
        flash(f'Equipment {_equipment.name} with id {id} is currently in use by {_equipment.get_current_active_usage().user}!', 'danger')
        return redirect("/equipment/my_page") #return redirect(url_for('equipment.view_equipment', id=_equipment.id))
    
    if _equipment.is_usable==False:
        _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
        flash(f'Equipment {_equipment.name} with id {id} is currently not usable. Please contact {_resp_user.name}!', 'danger')
        return redirect("/equipment/my_page") #return redirect(url_for('equipment.view_equipment', id=_equipment.id))
        
    if _form.validate_on_submit():
        _equipment=EquipmentModel.query.filter_by(id=_form.borrowing_equipment.data).first()
        _user=Users.query.filter_by(id=_form.user.data).first()
        _usage_location=StorageModel.query.filter_by(id=_form.usage_location_id.data).first()
        _equipment.borrow_equipment(
            name=_form.name.data,
            usage_start= _form.usage_start_datetime.data,
            usage_planned_end= _form.alt1_usage_planned_end_date.data,
            #usage_duration_days= _form.alt2_usage_duration_days.data,
            borrowing_user=_user,
            usage_location = _usage_location,
            )
        flash(f'Borrowing Equipment successful.', 'success')

    flash(f'You can borrow this equipment. Please add some spicy infos.', 'secondary')
    return render_template('equipment/borrow_equipment.html', form=_form, equipment=_equipment)

@equipment.route('/borrow_multiples', methods=['GET', 'POST'])
@login_required
def borrow_multiple_equipments():
    storages = StorageModel.query.filter_by(room_id=1).all()
    equipments = EquipmentModel.query.filter_by(is_usable=True).all()
    users = Users.query.all()
    is_not_in_use_equipments=[]
    for equipment in equipments:
        if equipment.is_in_use()==False:
            is_not_in_use_equipments.append(equipment)
            
    _form = BorrowMultipleEquipmentsForm()
    _form.usage_location_id.choices = [(storage.id, storage.name) for storage in storages]
    _form.alt1_usage_planned_end_date.data = datetime.date.today() + datetime.timedelta(days=1)
    _form.name.data = "experimentname"
    _form.user.choices = [(user.id, user.name) for user in users]
    _form.borrowing_equipments.choices = [(equipment.id, equipment.name) for equipment in is_not_in_use_equipments]  
    
    if _form.validate_on_submit():
        _borrowing_equipments = _form.borrowing_equipments.data

        for _equipment_id in _borrowing_equipments:

            if _equipment_id is None:
                flash(f'Equipment with id {_equipment_id} does not exist!', 'danger')
                bool_stopper = True
            else:
                _equipment = EquipmentModel.query.filter_by(id=int(_equipment_id)).first()
                bool_stopper = False
                if _equipment is None:
                    flash(f'Equipment {_equipment.name} with id {_equipment.id} does not exist!', 'danger')
                    bool_stopper = True
                
                if _equipment.is_in_use():
                    flash(f'Equipment {_equipment.name} with id {_equipment.id} is currently in use by {_equipment.get_current_active_usage().user}!', 'danger')
                    bool_stopper = True
                
                if _equipment.is_usable==False:
                    _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
                    flash(f'Equipment {_equipment.name} with id {_equipment.id} is currently not usable. Please contact {_resp_user.name}!', 'danger')
                    bool_stopper = True

                if bool_stopper == False:
                    _equipment=EquipmentModel.query.filter_by(id=_equipment_id).first()
                    _user=Users.query.filter_by(id=_form.user.data).first()
                    _usage_location=StorageModel.query.filter_by(id=_form.usage_location_id.data).first()
                    _equipment.borrow_equipment(
                        name=_form.name.data,
                        usage_start= _form.usage_start_datetime.data,
                        usage_planned_end= _form.alt1_usage_planned_end_date.data,
                        borrowing_user=_user,
                        usage_location = _usage_location,
                        )
                    flash(f'Borrowing Equipment {_equipment.name} with id {_equipment.id} was succesful.', 'success')
        flash(f'Borrowing multiple equipments process finished.', 'warning')
    return render_template('equipment/borrow_multiple_equipments.html', form=_form)

@equipment.route('/return/<id>', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    
    if _equipment is None:
        flash(f'Equipment {_equipment.name} with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    if _equipment.is_in_use() ==False:
        flash(f"Equipment {_equipment.name} with id {id} cannot be returned, since it has not been borrowed.", 'danger')
        return redirect(url_for("equipment.my_page"))
            
    if not _equipment.is_in_use_by(current_user) and not current_user.role_code==ADMIN:
        flash(f'Equipment {_equipment.name} with id {id} has not been borrowed by you.', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    _equipment.return_equipment()
    flash(f'Equipment {_equipment.name} has been returned succesfuly.', 'success')
    return redirect(url_for("equipment.my_page"))
    
@equipment.route('/brief/<id>', methods=['GET', 'POST'])
@login_required
def add_briefing(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
    admins = Users.query.filter_by(role_code=ADMIN).all()
    users = Users.query.all()
    equipments = EquipmentModel.query.all()
    if not current_user.role_code==ADMIN:
        flash(f'Sorry, Admin only can add briefings this equipment {_equipment.name} with id {id}. Please contact {_resp_user.name}!', 'danger')
        return redirect(url_for("equipment.my_page"))
    _form = AddBriefingForm()
    _form.briefed_user_id.choices = [(user.id, user.name) for user in users]
    _form.briefer_id.choices = [(user.id, user.name) for user in admins]
    _form.briefer_id.default = current_user.id
    _form.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
    _form.equipment_id.default = _equipment.id #(_equipment.id, _equipment.name)
    if _form.validate_on_submit():
        _equipment=EquipmentModel.query.filter_by(id=_form.equipment_id.data).first()
        _briefed_user=Users.query.filter_by(id=_form.briefed_user_id.data).first()
        _briefer=Users.query.filter_by(id=_form.briefer_id.data).first()
        _equipment.add_briefing(
            date = _form.date.data,
            text = _form.text.data,
            date_until = _form.date_until.data,
            user=_briefed_user,
            briefer=_briefer,
            )
        flash(f'Briefing submission succesful.', 'success')
    return render_template('equipment/add_briefing.html',
                           form=_form,
                           equipment=_equipment,
                           )                   
            
            
@equipment.route('/comment/<id>', methods=['GET', 'POST'])
@login_required
def add_comment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    equipments = EquipmentModel.query.all()
    _form = AddCommentForm()
    _form.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
    _form.equipment_id.default = _equipment.id #(_equipment.id, _equipment.name)
    if _form.validate_on_submit():
        _equipment=EquipmentModel.query.filter_by(id=_form.equipment_id.data).first()
        
        _equipment.add_comment(
            date = get_current_time(),
            text = _form.comment.data,
            user= current_user,
            is_comment_for_responsible_admin= True, 
            is_comment_for_users= True,
            )
        flash(f'Comment submission succesful.', 'success')

    return render_template('equipment/add_comment.html',
                           form=_form,
                           equipment=_equipment,
                           )                   
            
@equipment.route('/calibrate/<id>', methods=['GET', 'POST'])
@login_required
def add_calibration(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    equipments = EquipmentModel.query.all()
    _form = AddCalibrationForm()
    _form.equipment_id.choices = [(equipment.id, equipment.name) for equipment in equipments]
    _form.equipment_id.default = _equipment.id #(_equipment.id, _equipment.name)
    if _form.validate_on_submit():
        _equipment=EquipmentModel.query.filter_by(id=_form.equipment_id.data).first()
        
        _equipment.add_calibration(
            date = _form.date.data,
            text = _form.comment.data,
            user= current_user,
            date_until= _form.date_until.data, 
            )
        flash(f'Calibration submission succesful.', 'success')
    return render_template('equipment/add_calibration.html',
                           form=_form,
                           equipment=_equipment,
                           ) 
             
@equipment.route('/kicker', methods=['GET', 'POST'])
@login_required
def kicker():
    _users = Users.query.all()
    _matches = KickerMatchModel.query.all()
    _form = KickerMatchForm()
    _form.team_1_player_1.choices = [(user.id, user.name) for user in _users]
    _form.team_1_player_1.default = current_user.id #(_equipment.id, _equipment.name)
    _form.goals_team_1.data = 0
    _form.goals_team_2.data = 0
    
    _form.team_1_player_2.choices = [(user.id, user.name) for user in _users]
    _form.team_2_player_1.choices = [(user.id, user.name) for user in _users]
    _form.team_2_player_2.choices = [(user.id, user.name) for user in _users]
    if _form.validate_on_submit():
        _team_1_player_1 = Users.query.filter_by(id=_form.team_1_player_1.data).first()
        _team_1_player_2 = Users.query.filter_by(id=_form.team_1_player_2.data).first()
        _team_2_player_1 = Users.query.filter_by(id=_form.team_2_player_1.data).first()
        _team_2_player_2 = Users.query.filter_by(id=_form.team_2_player_2.data).first()
        _goals_team1 = _form.goals_team_1.data
        _goals_team2 = _form.goals_team_2.data
        _equipment=EquipmentModel.query.first()
        _equipment.add_kicker_match(
            _team_1_player_1=_team_1_player_1,
            _team_1_player_2=_team_1_player_2,
            _team_2_player_1=_team_2_player_1,
            _team_2_player_2=_team_2_player_2,
            _goals_team1 = _goals_team1,
            _goals_team2 = _goals_team2,
        )
        _matches = KickerMatchModel.query.all()
        flash(f'Kicker match submission successful.', 'success')

    return render_template('equipment/kicker_match.html',
                           form=_form,
                           user=current_user,
                           users=_users,
                           matches=_matches,
                           )
                  
@equipment.route('/kicker_scores', methods=['GET', 'POST'])
@login_required
def kicker_scoreboard():
    _users = Users.query.all()
    _matches = KickerMatchModel.query.all()
    return render_template('equipment/kicker_scoreboard.html',
                           user=current_user,
                           users=_users,
                           matches=_matches,
                           )
                  