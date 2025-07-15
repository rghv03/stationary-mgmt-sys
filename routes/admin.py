from flask import Blueprint, render_template, request, redirect, session, flash, send_file
from sqlalchemy import func
from datetime import datetime
import pandas as pd
from io import BytesIO
from models import User, RequestModel, MonthlyRequest, Department
from extensions import db

admin_bp = Blueprint('admin', __name__)

name_of_items = [
    "Photo Copier paper A-4 Size", "Pencil HB", "Pencil Eraser", "Sharpener", "Scale", "Vim Powder",
    "Stapler Pin (Big)", "Stapler Pin (Small)", "Stapler Small", "Stapler Big", "Note pad", "Room freshener",
    "Hit Spray", "Colin Spray", "Envelope (Small)", "Envelope (Big)", "File Cover", "Index Folder",
    "Ball Pen (Blue)", "Gel Pen", "Tape (Big)", "Tape (Small)", "White Fluid", "Hand Soap", "Dettol Hand wash Liquid", 
    "Glue Stick", "White Duster", "Yellow Duster", "Glass Tumbler", "High lighter", "Permanent Marker", "C.D", "Noting Sheet",
    "Dust Bin", "Register (Big)", "Register (Medium)", "Register (Small)", "Color Post-it Pad (Tree Color)",
    "Post-it Pad (Yellow)", "Peon book", "Hand Towel", "Towel Big", "Scissor", "Single Punch", "Double Punch",
    "Fevicol", "Gum Bottle", "U Clip", "Inkpad", "Pin Box (cushion)", "Green Tag", "White Tag", "File Binder",
    "Paper Weight", "Pencil Cell"
]

@admin_bp.route('/admin_home')
def admin_home():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    user = User.query.get(session['user_id'])
    return render_template('admin_home.html', role='admin', user=user)

@admin_bp.route('/monthly-requests', methods=['GET', 'POST'])
def monthlyrequests():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        items_data = []
        for item in name_of_items:
            safe_item = item.replace(' ','_').replace('.','').replace('-','_')
            qty = request.form.get(f'qty_{safe_item}')
            remarks = request.form.get(f'remarks_{safe_item}','')
            quantity = int(qty) if qty and qty.isdigit() else 0
            items_data.append({
                'item': item,
                'quantity': quantity,
                'remarks': remarks if remarks else '-',
                'quantity_issued': 0
            })
        user = User.query.get(session['user_id'])
        monthly_req = MonthlyRequest(
            user_id=session['user_id'],
            month=datetime.now().strftime('%B'),
            year=datetime.now().year,
            items=items_data,
            date_requested=datetime.now(),
            department_name=user.department_name
        )
        db.session.add(monthly_req)
        db.session.commit()
        flash("Request Submitted ✅", "success")
        return redirect('/monthly-requests')
    return render_template('monthly_req.html', items=name_of_items, role='admin')

@admin_bp.route('/admin/monthly-requests-view')
def admin_monthly_requests_view():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    user_id = session['user_id']
    month_year = request.args.get('month_year')
    selected_month_year = month_year
    query = MonthlyRequest.query.filter_by(user_id=user_id)
    if month_year:
        year, month = month_year.split('-')
        query = query.filter(
            func.strftime('%Y', MonthlyRequest.date_requested) == year,
            func.strftime('%m', MonthlyRequest.date_requested) == month
        )
    monthly_requests = query.order_by(MonthlyRequest.date_requested.desc()).all()
    return render_template('admin_monthly_requests.html', requests=monthly_requests, role='admin', selected_month_year=selected_month_year)

@admin_bp.route('/admin/monthly-request/<int:req_id>')
def admin_view_monthly_request(req_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    return render_template('admin_monthly_request_print.html', req=req, user=req.user, role='admin')

@admin_bp.route('/admin/monthly-request/<int:req_id>/edit', methods=['GET', 'POST'])
def edit_monthly_req(req_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    show_alert = False
    if request.method == 'POST':
        items_data = []
        for item in name_of_items:
            safe_item = item.replace(' ','_').replace('.','').replace('-','_')
            qty = request.form.get(f'qty_{safe_item}')
            remarks = request.form.get(f'remarks_{safe_item}','')
            quantity = int(qty) if qty and qty.isdigit() else 0
            items_data.append({
                'item': item,
                'quantity': quantity,
                'remarks': remarks if remarks else '-',
                'quantity_issued': 0
            })
        req.items = items_data
        req.date_requested = datetime.now()
        req.ad_status = 'Pending'
        req.lab_incharge_status = 'Pending'
        db.session.commit()
        show_alert = True
    item_dict = {i['item']: i for i in req.items}
    return render_template('edit_monthly_request.html', show_alert=show_alert, items=name_of_items, req=req, item_dict=item_dict, role='admin')

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    admin_user = User.query.get(session['user_id'])
    admin_dept = admin_user.department_name
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
    date_str = request.args.get('date')
    status = request.args.get('status')
    invalid_date = False
    if status and status != "All":
        query = RequestModel.query.join(User).filter(User.department_name == admin_dept).filter(RequestModel.status == status)
    else:
        query = RequestModel.query.join(User).filter(User.department_name == admin_dept)
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            selected_date = None
            invalid_date = True
    else:
        selected_date = None
    requests = query.order_by(RequestModel.date_requested.desc()).all()
    no_results = len(requests) == 0 and not invalid_date
    return render_template('admin_dash.html', requests=requests, departments=[admin_dept], selected_dept=admin_dept, selected_date_str=date_str, selected_status=status, selected_date=selected_date, invalid_date=invalid_date, no_results=no_results, role='admin')

@admin_bp.route('/admin/export')
def export_requests():
    department_name = request.args.get('department')
    date_str = request.args.get('date')
    status = request.args.get('status')
    query = RequestModel.query.join(User).join(Department, User.department_name == Department.shortname)
    if department_name:
        query = query.filter(User.department_name == department_name)
    if status and status != "All":
        query = query.filter(RequestModel.status == status)
    if date_str and date_str.strip():
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            return "Invalid date", 400
    requests = query.all()
    data = [{
        "Sr no.": i,
        "Name of Items": r.item,
        "Quantity Demanded": r.quantity,
        "Quantity Issued": r.quantity_issued,
        "Remarks": r.remarks,
    } for i, r in enumerate(requests, start=1)]
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    return send_file(output, download_name='Stationary_requests.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 