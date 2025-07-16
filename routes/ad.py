from flask import Blueprint, render_template, request, redirect, session, flash
from models import User, Department, MonthlyRequest
from extensions import db

ad_bp = Blueprint('ad', __name__)


@ad_bp.route('/ad/monthly-requests')
def ad_monthly_requests():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    user_id = session.get('user_id')
    departments = Department.query.filter(
        (Department.head_id == user_id) | (Department.ad_id == user_id)
    ).all()
    department_names = [d.shortname for d in departments]
    requests = (
        MonthlyRequest.query
        .join(User, MonthlyRequest.user_id == User.id)
        .filter(
            MonthlyRequest.department_name.in_(department_names),
            User.role == 'admin'
        )
        .order_by(MonthlyRequest.date_requested.desc())
        .all()
    )
    user = User.query.get(session['user_id'])
    return render_template('ad_monthly_requests.html', requests=requests, role=session.get('role'), user=user)

@ad_bp.route('/ad/monthly-request/<int:req_id>/action', methods=['POST'])
def ad_action_monthly_requests(req_id):
    if 'user_id' not in session:
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    action = request.form.get('action')
    if action == 'approve':
        req.ad_status = 'Approved'
    elif action == 'reject':
        req.ad_status = 'Rejected'
    db.session.commit()
    flash("Request Updated.", "success")
    return redirect('/ad/monthly-requests')

@ad_bp.route('/ad/monthly-request/<int:req_id>')
def ad_view_monthly_request(req_id):
    if 'user_id' not in session:
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    return render_template('ad_monthly_request_view.html', req=req, user=req.user, role=session.get('role')) 