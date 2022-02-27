# -*- coding: utf-8 -*-

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from ame_manager_app.equipment.forms import BorrowEquipmentForm

from ame_manager_app.equipment.models import EquipmentModel, StorageModel
from ame_manager_app.user import ADMIN

from ..extensions import db

equipment = Blueprint("equipment", __name__, url_prefix="/equipment")


@equipment.route('/my_equipment', methods=['GET', 'POST'])
@login_required
def my_equipment():
    _responsible_equipment = EquipmentModel.query.filter_by(user_id=current_user.id).all()
    _borrowed_equipment = EquipmentModel.query.filter_by(user_id=current_user.id).all()

    return render_template('equipment/my_equipment.html',
                           responsible_equipment=_responsible_equipment,
                           borrowed_equipment=_borrowed_equipment,
                           )


@equipment.route('/equipment/<id>', methods=['GET', 'POST'])
def view_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id, user_id=current_user.id).all()

    return render_template('equipment/view_equipment.html',
                           equipment=_equipment,
                           )

@equipment.route('/borrow_equipment/<id>', methods=['GET', 'POST'])
@login_required
def borrow_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id, user_id=current_user.id).first()
    
    if _equipment is None:
        flash(f'Equipment with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_equipment"))
        
    if _equipment.is_in_use():
        flash(f'Equipment with id {id} is currently in use by {_equipment.get_current_active_usage().user}!', 'danger')
        return redirect(url_for("equipment.my_equipment"))
    
    _form = BorrowEquipmentForm()

    if _form.validate_on_submit():
        _usage_location = StorageModel.query.filter_by(id=_form.storage_id).first()
        _equipment.borrow_equipment(user=current_user,
                                    usage_location=_usage_location,
                                    name=_form.name,
                                    usage_duration_days=_form.usage_duration_days,
                                    )
    
    flash(f'Equipment has been borrowed successfully.', 'success')
    return render_template('equipment/my_equipment.html', form=_form, _equipment=_equipment)


@equipment.route('/return_equipment/<id>', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    _equipment:EquipmentModel = EquipmentModel.query.filter_by(id=id).first()
    
    if _equipment is None:
        flash(f'Equipment with id {id} does not exist!', 'danger')
        return redirect(url_for("equipment.my_equipment"))
        
    if not _equipment.is_in_use_by(current_user) and not current_user.role_code==ADMIN:
        flash(f'Equipment with id {id} has not been borrowed by you.', 'danger')
        return redirect(url_for("equipment.my_equipment"))
    
    _equipment.return_equipment()
    flash(f'Equipment has been returned successfully.', 'success')
    return redirect(url_for("equipment.my_equipment"))