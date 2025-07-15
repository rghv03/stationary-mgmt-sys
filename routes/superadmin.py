from flask import Blueprint, render_template, request, redirect, session, flash
from models import User, Department, RequestModel
from extensions import db
from werkzeug.security import generate_password_hash
from sqlalchemy import func
from datetime import datetime

superadmin_bp = Blueprint('superadmin', __name__)

@superadmin_bp.route('/superadmin')
def superadmin_dashboard():
    if 'user_id' not in session or session.get('role') != 'superadmin':
        return redirect('/login')
    users = User.query.all()
    current_user = User.query.get(session['user_id'])
    return render_template('superadmin_dash.html', users=users, role='superadmin', user=current_user)

@superadmin_bp.route('/manage_requests', methods=['GET', 'POST'])
def manage_requests():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    if request.method == 'POST':
        req_id = request.form.get('request_id')
        action = request.form.get('action')
        quantity_issued = request.form.get('quantity_issued')
        if req_id and action:
            request_obj = RequestModel.query.get(req_id)
            if request_obj:
                if action == 'approve':
                    request_obj.status = 'Approved by Superadmin' if session.get('role') == 'superadmin' else "Approved"
                    request_obj.quantity_issued = int(quantity_issued)
                elif action == 'reject':
                    if session.get('role') == 'superadmin':
                        request_obj.status = 'Rejected by Superadmin'
                    else:
                        request_obj.status = 'Rejected'
                db.session.commit()
    department = request.args.get('department')
    selected_date = None
    date_str = request.args.get('date')
    status = request.args.get('status')
    query = RequestModel.query.join(User)
    invalid_date = False
    if status and status != "All":
        query = query.filter(RequestModel.status == status)
    if department:
        query = query.filter(User.department_name == department)
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            invalid_date = True
    requests = query.order_by(RequestModel.date_requested.desc()).all()
    no_results = len(requests) == 0 and not invalid_date
    departments = [d.shortname for d in Department.query.order_by(Department.shortname).all()]
    return render_template('manage_requests.html', requests=requests, departments=departments, selected_dept=department, selected_date_str=date_str, selected_status=status, selected_date=selected_date, invalid_date=invalid_date, no_results=no_results, role='superadmin')

@superadmin_bp.route('/manage_users')
def manage_users():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    users = User.query.all()
    departments = Department.query.all()
    return render_template('manage_users.html', users=users, role='superadmin', departments=departments)

DESIGNATIONS = [
    "Technical Officer 'B'",
    "Scientist 'B'",
    "Scientist 'C'",
    "Scientist 'D'",
    "Scientist 'E'",
    "Scientist 'F'",
    "Scientist 'G'"
]

@superadmin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    departments = Department.query.all()
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        designation = request.form['designation']
        department_name = request.form['department_name']
        existing = User.query.filter_by(username=username).first()
        if not existing:
            user = User(first_name=first_name, middle_name=middle_name, last_name=last_name, username=username, password=password, role=role, department_name=department_name, designation=designation)
            db.session.add(user)
            db.session.commit()
            flash("User added Succesfully")
        else:
            flash("Username already exists")
        return redirect('/manage_users')
    return render_template('add_user.html', role='superadmin', departments=departments, designations=DESIGNATIONS)

@superadmin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('role') != 'superadmin':
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    departments = Department.query.all()
    designations = DESIGNATIONS
    roles = ['employee', 'admin']
    add_roles = ['None', 'Group AD', 'Group Head']
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.middle_name = request.form['middle_name']
        user.last_name = request.form['last_name']
        user.username = request.form['username']
        user.designation = request.form['designation']
        user.department_name = request.form['department_name']
        user.role = request.form['role']
        user.is_lab_stationary = bool(request.form.get('is_lab_stationary'))
        selected_add_role = request.form.get('add_roles')
        selected_dept_shortname = user.department_name
        dept = Department.query.filter_by(shortname=selected_dept_shortname).first()
        if dept:
            if selected_add_role == 'Group AD':
                dept.ad_id = user.id
            elif selected_add_role == 'Group Head':
                dept.head_id = user.id
            elif selected_add_role == 'None':
                if dept.ad_id == user.id:
                    dept.ad_id = None
                elif dept.head_id == user.id:
                    dept.head_id = None
        db.session.commit()
        flash("User updated successfully!")
        return redirect('/manage_users')
    return render_template('edit_user.html', user=user, role='superadmin', departments=departments, designations=designations, roles=roles, add_roles=add_roles)

@superadmin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'superadmin':
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    if user.requests:
        flash("Cannot delete user who has submitted requests")
        return redirect('/manage_users')
    else:
        db.session.delete(user)
        db.session.commit()
    flash("User deleted")
    return redirect('/manage_users') 