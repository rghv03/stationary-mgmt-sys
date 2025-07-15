from flask import Blueprint, render_template, request, redirect, session
from models import User, RequestModel
from extensions import db

employee_bp = Blueprint('employee', __name__)

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

@employee_bp.route('/employee', methods=['GET', 'POST'])
def employee_dashboard():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    show_alert = False
    if request.method == 'POST':
        item = request.form['item']
        quantity = request.form['quantity']
        remarks = request.form['remarks']
        user = User.query.get(session['user_id'])
        new_request = RequestModel(user_id=user.id, item=item, quantity=int(quantity), remarks=remarks)
        db.session.add(new_request)
        db.session.commit()
        show_alert = True
    current_user = User.query.get(session['user_id'])
    return render_template('Emp_dash.html', role='employee', current_user=current_user, items=name_of_items, show_alert=show_alert)

@employee_bp.route('/view-requests')
def view_employee_requests():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    user_id = session['user_id']
    my_requests = RequestModel.query.filter_by(user_id=user_id).order_by(RequestModel.date_requested.desc()).all()
    return render_template('emp_view_requests.html', requests=my_requests, role='employee') 