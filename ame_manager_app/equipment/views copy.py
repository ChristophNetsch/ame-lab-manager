# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from ..extensions import db
from ..utils import get_current_time

from .forms import MyTaskForm
from .models import EquipmentModel, UsageModel


equipment = Blueprint('equipment', __name__, url_prefix='/equipment')


@equipment.route('/equipment-usage', methods=['GET', 'POST'])
@login_required
def borrowed_equipment():

    _borrowed_devices = EquipmentModel.query.filter_by(current_user_id=current_user.id).all()

    return render_template('equipment/my_tasks.html',
                           all_tasks=_borrowed_devices,
                           _active_tasks=True)


@equipment.route('/equipment-responsibilities', methods=['GET', 'POST'])
@login_required
def responsible_equipment():

    _borrowed_devices = EquipmentModel.query.filter_by(responsible_user_id=current_user.id).all()

    return render_template('equipment/my_tasks.html',
                           all_tasks=_borrowed_devices,
                           _active_tasks=True)
    

@equipment.route('/view_equipment/<id>', methods=['GET', 'POST'])
@login_required
def view_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id).first()

    if not _equipment:
        flash('Oops! Something went wrong!.', 'danger')
        return redirect(url_for("equipment.borrowed_equipment"))

    return render_template('equipment/view_task.html',
                           task=_equipment)


@equipment.route('/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment():

    _equipment = EquipmentModel()

    _form = MyTaskForm()

    if _form.validate_on_submit():

        _equipment.users_id = current_user.id

        _form.populate_obj(_equipment)

        db.session.add(_equipment)
        db.session.commit()

        db.session.refresh(_equipment)
        flash('Your Device is added successfully!', 'success')
        return redirect(url_for("equipment.borrowed_equipment"))

    return render_template('equipment/add_task.html', form=_form, _active_tasks=True)


@equipment.route('/borrow-equipment/<id>', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id, is_in_use=True).last()

    if not _equipment:
        flash('Oops! Something went wrong!.', 'danger')
        return redirect(url_for("equipment.my_tasks"))
    
    _usage = UsageModel()
    _equipment.usage.is_in_use = False    
    _equipment.usage.return_date = get_current_time()
    
    db.session.add(_equipment)
    db.session.commit()

    flash('Your Device is deleted successfully!', 'success')
    return redirect(url_for('equipment.my_tasks'))


@equipment.route('/return-equipment/<id>', methods=['GET', 'POST'])
@login_required
def return_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id, is_in_use=True).last()

    if not _equipment:
        flash('Oops! Something went wrong!.', 'danger')
        return redirect(url_for("equipment.my_tasks"))
    
    _equipment.usage.is_in_use = False    
    _equipment.usage.return_date = get_current_time()
    
    db.session.add(_equipment)
    db.session.commit()

    flash('Your Device is deleted successfully!', 'success')
    return redirect(url_for('equipment.my_tasks'))


@equipment.route('/edit-equipment/<id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id):
    _equipment = EquipmentModel.query.filter_by(id=id).first()

    if not _equipment:
        flash('Oops! Something went wrong!.', 'danger')
        return redirect(url_for("equipment.my_tasks"))

    _form = MyTaskForm(obj=_equipment)

    if _form.validate_on_submit():
        _form.populate_obj(_equipment)

        db.session.add(_equipment)
        db.session.commit()

        flash('Your Device updated successfully!', 'success')
        return redirect(url_for("equipment.my_tasks"))

    return render_template('equipment/edit_task.html', form=_form, task=_equipment, _active_tasks=True)
