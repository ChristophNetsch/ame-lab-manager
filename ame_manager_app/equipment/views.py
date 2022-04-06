# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from ame_manager_app.equipment.forms import BorrowEquipmentForm

from ame_manager_app.equipment.models import EquipmentModel, StorageModel, UsageModel, RoomModel
from ame_manager_app.user import ADMIN
from ame_manager_app.user.models import Users

from ..extensions import db

equipment = Blueprint("equipment", __name__, url_prefix="/equipment")


@equipment.route('/my_page', methods=['GET', 'POST'])
@login_required
def my_page():
    _usages = UsageModel.query.filter_by(user_id=current_user.id).all()
    _responsible_equipments = EquipmentModel.query.filter_by(responsible_user_id=current_user.id).all()
    _responsible_storages = StorageModel.query.filter_by(responsible_user_id=current_user.id).all()
    _responsible_rooms = RoomModel.query.filter_by(responsible_user_id=current_user.id).all()

    return render_template('equipment/my_page.html',
                           user = current_user,
                           responsible_equipments=_responsible_equipments,
                           usages=_usages,
                           storages = _responsible_storages,
                           rooms = _responsible_rooms,
                           )

@equipment.route('/view_equipment/<id>', methods=['GET', 'POST'])
def view_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _equipment.responsible_user_id).first()
    return render_template('equipment/view_equipment.html',
                           equipment=_equipment,
                           resp_user = _resp_user,
                           )

@equipment.route('/view_room/<id>', methods=['GET', 'POST'])
def view_room(id):
    _room = RoomModel.query.filter_by(id=id).first()
    _storages = StorageModel.query.filter_by(room_id=id).all()
    _resp_user = Users.query.filter(Users.id == _room.responsible_user_id).first()
    _all_equipment_from_storages=[]
    _in_use_equipment_from_storages=[]
    _usable_equipment_from_storages=[]
    for _storage in _storages:
        _all_equipment_from_storages.append(EquipmentModel.query.filter(EquipmentModel.id == _storage.id).all())
        _in_use_equipment_from_storages.append(EquipmentModel.query.filter(EquipmentModel.id == _storage.id, EquipmentModel.is_usable==False).all())
        _usable_equipment_from_storages.append(EquipmentModel.query.filter(EquipmentModel.id == _storage.id, EquipmentModel.is_usable==True).all())
    return render_template('equipment/room_page.html',
                           room=_room,
                           storages = _storages,
                           resp_user = _resp_user,
                           all_equipment = _all_equipment_from_storages,
                           usable_equipment = _usable_equipment_from_storages,
                           in_use_equipment = _in_use_equipment_from_storages,
                           )

@equipment.route('/view_storage/<id>', methods=['GET', 'POST'])
def view_storage(id):
    _storage = StorageModel.query.filter_by(id=id).first()
    _resp_user = Users.query.filter(Users.id == _storage.responsible_user_id).first()
    _all_equipment_from_storage = EquipmentModel.query.filter(EquipmentModel.id == _storage.id).all()
    _in_use_equipment_from_storage = EquipmentModel.query.filter(EquipmentModel.id == _storage.id, EquipmentModel.is_usable==False).all()
    _usable_equipment_from_storage = EquipmentModel.query.filter(EquipmentModel.id == _storage.id, EquipmentModel.is_usable==True).all()
    return render_template('equipment/storage_page.html',
                           storage=_storage,
                           resp_user = _resp_user,
                           usable_equipment = _usable_equipment_from_storage,
                           in_use_equipment = _in_use_equipment_from_storage,
                           all_equipment = _all_equipment_from_storage,
                           )

@equipment.route('/borrow_equipment/<id>', methods=['GET', 'POST'])
@login_required
def borrow_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    
    if _equipment is None:
        flash(f'Equipment with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    if _equipment.is_in_use():
        flash(f'Equipment with id {id} is currently in use by {_equipment.get_current_active_usage().user}!', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    _form = BorrowEquipmentForm()

    if _form.validate_on_submit():
        _usage_location = StorageModel.query.filter_by(id=_form.storage_id).first()
        _equipment.borrow_equipment(user=current_user,
                                    usage_location=_usage_location,
                                    name=_form.name,
                                    usage_duration_days=_form.usage_duration_days,
                                    )
    
    flash(f'Equipment has been borrowed successfully.', 'success')
    return render_template('equipment/my_page.html', form=_form, _equipment=_equipment)


@equipment.route('/return_equipment/<id>', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    
    if _equipment is None:
        flash(f'Equipment with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_page"))
        
    if not _equipment.is_in_use_by(current_user) and not current_user.role_code==ADMIN:
        flash(f'Equipment with id {id} has not been borrowed by you.', 'danger')
        return redirect(url_for("equipment.my_page"))
    
    _equipment.return_equipment()
    flash(f'Equipment has been returned successfully.', 'success')
    return redirect(url_for("equipment.my_page"))