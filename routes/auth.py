from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if getattr(user, 'is_lab_stationary', False):
                return redirect('/lab_incharge/monthly-requests')
            return redirect('/Dashboard')
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error, role=None)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@auth_bp.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if 'user_id' not in session:
        return redirect('/signup')
    user = User.query.get(session['user_id'])
    error = None
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if not check_password_hash(user.password, old_password):
            error = "Old password is Incorrect!!!"
        elif new_password != confirm_password:
            error = "New passwords do not match"
        else:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password Updated successfully.")
            return redirect('/login')
    return render_template('change_password.html', error=error, role=session.get('role'), is_lab_stationary=getattr(user, 'is_lab_stationary', False))

@auth_bp.route('/Dashboard')
def dashboard():
    role = session.get('role')
    if not role:
        return redirect('/login')

    if role == 'superadmin':
        return redirect('/superadmin')
    elif role == 'admin':
        return redirect('/admin_home')
    elif role == 'employee':
        user = User.query.get(session['user_id'])
        if getattr(user, 'is_lab_stationary', False):
            return redirect('/lab_incharge/monthly-requests')
        else:
            return redirect('/employee')
    else:
        return redirect('/login') 