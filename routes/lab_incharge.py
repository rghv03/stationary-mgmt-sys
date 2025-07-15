from flask import Blueprint, render_template, request, redirect, session
from sqlalchemy import func
from datetime import datetime
from models import User, Department, MonthlyRequest
from extensions import db
from sqlalchemy.orm.attributes import flag_modified

lab_incharge_bp = Blueprint('lab_incharge', __name__)

@lab_incharge_bp.route('/lab_incharge/monthly-requests', methods=['GET', 'POST'])
def lab_incharge_monthly_requests():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    if not user.is_lab_stationary:
        return redirect('/login')
    department = request.args.get('department')
    month_year = request.args.get('month_year')
    selected_month_year = month_year
    query = MonthlyRequest.query.filter_by(ad_status='Approved')
    if month_year:
        year, month = month_year.split('-')
        query = query.filter(
            func.strftime('%Y', MonthlyRequest.date_requested) == year,
            func.strftime('%m', MonthlyRequest.date_requested) == month)
    if department:
        query = query.filter(MonthlyRequest.department_name == department)
    requests = query.order_by(MonthlyRequest.date_requested.desc()).all()
    no_results = len(requests) == 0
    departments = [d.shortname for d in Department.query.order_by(Department.shortname).all()]
    return render_template('lab_incharge_monthly_requests.html', requests=requests, selected_month_year=selected_month_year, role=session.get('role'), is_lab_stationary=True, departments=departments, selected_dept=department, no_results=no_results)

@lab_incharge_bp.route('/lab_incharge/monthly-request/<int:req_id>/edit', methods=['GET', 'POST'])
def lab_incharge_edit_monthly_request(req_id):
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    if not user.is_lab_stationary:
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    show_alert = False
    if request.method == 'POST':
        item_map = {item['item']: item for item in req.items}
        items_data = []
        for item in req.items:
            safe_item = item['item'].replace(' ', '_').replace('.', '').replace('-', '_')
            qty_issued = request.form.get(f'qty_issued_{safe_item}')
            item = item_map[item['item']]
            item['quantity_issued'] = int(qty_issued) if qty_issued and qty_issued.isdigit() else 0
            items_data.append(item)
        req.items = items_data
        flag_modified(req, 'items')
        req.lab_incharge_status = 'Issued'
        db.session.commit()
        show_alert = True
    return render_template('lab_incharge_edit_monthly_request.html', req=req, show_alert=show_alert, role='lab_stationary_incharge', is_lab_stationary=True)

@lab_incharge_bp.route('/lab_incharge/monthly-request/<int:req_id>/print')
def lab_incharge_print_monthly_request(req_id):
    if 'user_id' not in session:
        return redirect('/login')
    user = User.query.get(session['user_id'])
    if not user.is_lab_stationary:
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    return render_template('lab_incharge_monthly_request_print.html', req=req, user=req.user, role='lab_stationary_incharge', is_lab_stationary=True) 