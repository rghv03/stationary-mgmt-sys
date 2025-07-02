from flask import Flask, flash, redirect, render_template, request, session , send_file 
from werkzeug.security import check_password_hash,generate_password_hash
from models import User,db, RequestModel,MonthlyRequest,Department
from sqlalchemy import func,extract
from datetime import datetime
import pandas as pd
from io import BytesIO
from signup_route import signup_bp
from flask_migrate import Migrate


app = Flask(__name__)

app.config['SECRET_KEY']='rshandilya' 
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///stationary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(signup_bp)

@app.route('/')
def home():
    return redirect('/login')

#login route
@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() #returns data on condition of username, only first match else none 

        if user and check_password_hash(user.password , password):
            session['user_id'] = user.id
            session['role'] = user.role

            return redirect('/Dashboard')
        else:
            error = "Invalid username or password"
    return render_template('login.html', error = error, role = None )

#logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
#change password route
@app.route('/change_password', methods = ['POST','GET'])
def change_password():
    if 'user_id' not in session:
        return redirect('/signup')
    user = User.query.get(session['user_id'])
    error = None
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
    
        if not check_password_hash(user.password , old_password):
            error = "Old password is Incorrect!!!"
        elif new_password !=confirm_password:
            error = "New passwords do not match"
        else:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password Updated successfully.")
            return redirect('/change_password')
    return render_template('change_password.html', error = error , role = session.get('role'))


#Dashboard route
@app.route('/Dashboard')
def dashboard():
    role = session.get('role')
    if not role :
        return redirect('/login')
    

    if role == 'superadmin':
        return redirect('/superadmin')
    elif role == 'admin':
        return redirect('/admin_home')
    elif role == 'employee':
        return redirect('/employee')
    else:
        return redirect('/login')

#superadmin route
@app.route('/superadmin')
def superadmin_dashboard():
    if 'user_id' not in session or session.get('role') != 'superadmin':
        return redirect('/login')
    
    users = User.query.all()
    
    return render_template('/superadmin_dash.html',  users = users , role = 'superadmin')
#manage_requests route
@app.route('/manage_requests', methods=['GET','POST'] )
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
                    request_obj.status = 'Approved by Superadmin' if session.get('role')=='superadmin' else "Approved"
                    request_obj.quantity_issued = int(quantity_issued) 
                elif action == 'reject':
                    if session.get('role')=='superadmin':
                        request_obj.status = 'Rejected by Superadmin'
                    else:
                        request_obj.status = 'Rejected'
                db.session.commit()
    requests = RequestModel.query.all()
    #filters
    #adding filter option
    department = request.args.get('department')
    selected_date = None
    date_str = request.args.get('date')
    status = request.args.get('status') 
    query = RequestModel.query.join(User)
    invalid_date = False
    if status and status!="All":
        query = query.filter(RequestModel.status == status)
    if department:
        query = query.filter(User.department == department)
    
    if date_str:
        try:
            selected_date= datetime.strptime(date_str , '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            print("invalid date")
            invalid_date = True
    
    requests =  query.all()
    no_results = len(requests) == 0 and not invalid_date
    departments = [d[0] for d in db.session.query(User.department).distinct().all()]

    return render_template('manage_requests.html', requests=requests , departments = departments ,
                            selected_dept = department ,
                            selected_date_str = date_str , selected_status = status,
                            selected_date =selected_date , invalid_date = invalid_date ,
                            no_results = no_results,role='superadmin')


#manage-users route
@app.route('/manage_users')
def manage_users():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    
    users = User.query.all()
    # print("DEBUG: Users in DB ->")
    # for u in users:
    #     print(u.username, u.role, u.department)


    return render_template('manage_users.html', users = users , role = 'superadmin')
#adding user
@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        designation = request.form['designation']
        department = request.form['department']
        existing = User.query.filter_by(username=username).first()
        if not existing:
            user = User(username=username,password=password,role=role,department=department
                        ,designation=designation)
            db.session.add(user)
            db.session.commit()
            flash("User added Succesfully")
        else:
            flash("Username already exists")
        return redirect('/manage_users')
    return render_template('add_user.html',role='superadmin')
#editing user
@app.route('/edit_user/<int:user_id>',methods =['GET','POST'] )
def edit_user(user_id):
    if session.get('role') != 'superadmin':
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.designation = request.form['designation']
        user.department = request.form['department']
        user.role=request.form['role']
        db.session.commit()
        flash("User updated successfully!")
        return redirect('/manage_users')
    return render_template('edit_user.html', user=user,role='superadmin')

#deleting user
@app.route('/delete_user/<int:user_id>',methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'superadmin':
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    if user.requests:
        flash("Cannot delete user who has submitted requests")
        redirect ('/manage_users')
    else:
        db.session.delete(user)
        db.session.commit()
    flash("User deleted")
    return redirect('/manage_users')
#assigning AD or Head
@app.route('/assign_roles', methods=['GET','POST'])
def asign_roles():
    if session.get('role') != 'superadmin':
        return redirect('/login')
    departments = Department.query.all()
    users = User.query.all()
    message = None

    if request.method == 'POST':
        dept_id = request.form['department']
        ad_id = request.form.get('ad_id')
        head_id = request.form.get('head_id')
        # incharge_id = request.form.get('stationary_incharge_id')

        dept = Department.query.get(dept_id)
        if dept:
            dept.ad_id = ad_id if ad_id else None
            dept.head_id = head_id if head_id else None
            # dept.stationary_incharge_id = incharge_id if incharge_id else None
            db.session.commit()
            message = "Roles assigned successfully!"

    return render_template('assign_roles.html', departments=departments, users=users, message=message, role='superadmin')

#admin_home route
@app.route('/admin_home')
def admin_home():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_home.html', role = 'admin')

#items list
name_of_items = ["Photo Copier paper A-4 Size", "Pencil HB", "Pencil Eraser", "Sharpener", "Scale", "Vim Powder",
                "Stapler Pin (Big)", "Stapler Pin (Small)", "Stapler Small", "Stapler Big", "Note pad", "Room freshener",
                "Hit Spray", "Colin Spray", "Envelope (Small)", "Envelope (Big)", "File Cover", "Index Folder",
                "Ball Pen (Blue)", "Gel Pen", "Tape (Big)", "Tape (Small)", "White Fluid", "Hand Soap", "Dettol Hand wash Liquid", 
                "Glue Stick", "White Duster", "Yellow Duster", "Glass Tumbler", "High lighter", "Permanent Marker", "C.D", "Noting Sheet",
                "Dust Bin", "Register (Big)", "Register (Medium)", "Register (Small)", "Color Post-it Pad (Tree Color)",
                "Post-it Pad (Yellow)", "Peon book", "Hand Towel", "Towel Big", "Scissor", "Single Punch", "Double Punch",
                "Fevicol", "Gum Bottle", "U Clip", "Inkpad", "Pin Box (cushion)", "Green Tag", "White Tag", "File Binder",
                "Paper Weight", "Pencil Cell"]

#admin monthly route
#monthly request route
@app.route('/monthly-requests', methods=['GET','POST'] )
def monthlyrequests():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        today = datetime.today().day
        if today < 1 or today >10:
            flash("Requests can only be submitted within the first 10 days of the month.","danger")
            return redirect('/monthly-requests')
        items_data = []
        for item in name_of_items:
            safe_item = item.replace(' ','_').replace('.','').replace('-','_')
            qty = request.form.get(f'qty_{safe_item}')
            remarks = request.form.get(f'remarks_{safe_item}','')

            quantity = int(qty) if qty and qty.isdigit() else 0
            items_data.append({
                'item': item,
                'quantity': quantity,
                'remarks': remarks if remarks else '-'
            })
        user = User.query.get(session['user_id'])
        monthly_req = MonthlyRequest(
                user_id = session['user_id'],
                month=datetime.now().strftime('%B'),
                year = datetime.now().year,
                items =  items_data,
                date_requested = datetime.now(),
                department_id = user.department_id  
        )
        db.session.add(monthly_req)
        db.session.commit()
        flash("Request Submitted ✅","success")
        return redirect('/monthly-requests')
    return render_template('monthly_req.html', items = name_of_items,role='admin')

#admin view monthly requests
@app.route('/admin/monthly-requests-view')
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
    return render_template('admin_monthly_requests.html',requests=monthly_requests, role='admin', selected_month_year=selected_month_year)
#admin view/print
@app.route('/admin/monthly-request/<int:req_id>')
def admin_view_monthly_request(req_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    return render_template('admin_monthly_request_print.html', req=req ,user=req.user,role ='admin')
#admin edit request
@app.route('/admin/monthly-request/<int:req_id>/edit', methods=['GET','POST'])
def edit_monthly_req(req_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    show_alert = False
    if request.method == 'POST':
        today = datetime.today().day
        if today < 1 or today >10:
            flash("Requests can only be submitted within the first 10 days of the month.","danger")
            return redirect('/monthly-requests')
        items_data = []
        for item in name_of_items:
            safe_item = item.replace(' ','_').replace('.','').replace('-','_')
            qty = request.form.get(f'qty_{safe_item}')
            remarks = request.form.get(f'remarks_{safe_item}','')

            quantity = int(qty) if qty and qty.isdigit() else 0
            items_data.append({
                'item': item,
                'quantity': quantity,
                'remarks': remarks if remarks else '-'
            })
        req.items = items_data
        req.date_requested = datetime.now()
        db.session.commit()
        show_alert = True
    item_dict = {i['item']: i for i in req.items}
    return render_template('edit_monthly_request.html',show_alert = show_alert, items=name_of_items, req=req, item_dict=item_dict, role='admin')


#admin urgent request route
@app.route('/admin', methods = ['GET','POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect('/login')
    if request.method == 'POST':
        req_id = request.form.get('request_id')
        action = request.form.get('action')
        quantity_issued = request.form.get('quantity_issued')

        if req_id and action:
            request_obj = RequestModel.query.get(req_id)
            if request_obj:
                if action == 'approve':
                    request_obj.status = 'Approved by Superadmin' if session.get('role')=='superadmin' else "Approved"
                    request_obj.quantity_issued = int(quantity_issued) 
                elif action == 'reject':
                    if session.get('role')=='superadmin':
                        request_obj.status = 'Rejected by Superadmin'
                    else:
                        request_obj.status = 'Rejected'
                db.session.commit()
    #adding filter option
    department = request.args.get('department')
    selected_date = None
    date_str = request.args.get('date')
    status = request.args.get('status') 
    query = RequestModel.query.join(User)
    invalid_date = False
    if status and status!="All":
        query = query.filter(RequestModel.status == status)
    if department:
        query = query.filter(User.department == department)
    
    if date_str:
        try:
            selected_date= datetime.strptime(date_str , '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            print("invalid date")
            invalid_date = True
    
    requests =  query.order_by(RequestModel.date_requested.desc()).all()
    no_results = len(requests) == 0 and not invalid_date
    departments = [d[0] for d in db.session.query(User.department).distinct().all()]

    return render_template('admin_dash.html', requests=requests , departments = departments ,
                            selected_dept = department ,
                            selected_date_str = date_str , selected_status = status,
                            selected_date =selected_date , invalid_date = invalid_date ,
                            no_results = no_results,
                            role='admin')

#export excel route
@app.route('/admin/export')
def export_requests():
    department_id= request.args.get('department')
    date_str = request.args.get('date')
    status = request.args.get('status')

    query = RequestModel.query.join(User).join(Department, User.department_id == Department.id)

    if department_id:
        query = query.filter(User.department_id == department_id)
    if status and status!="All":
        query = query.filter(RequestModel.status == status)
    if date_str and date_str.strip():
        try:
            selected_date = datetime.strptime(date_str , '%Y-%m-%d').date()
            query = query.filter(func.date(RequestModel.date_requested) == selected_date)
        except ValueError:
            return "Invalid date" , 400
    requests = query.all()

    data = [{
        "Sr no." : i,
        "Name of Items":r.item,
        "Quantity Demanded": r.quantity,
        "Quantity Issued" : r.quantity_issued,
        "Remarks": r.remarks,
    } for i,r in enumerate(requests, start=1)]

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    return send_file(output, download_name='Stationary_requests.xlsx',
                      as_attachment = True,
                      mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


#employee route
@app.route('/employee',methods=['GET','POST'])
def employee_dashboard():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    show_alert = False
    if request.method == 'POST':

        item = request.form['item']
        quantity = request.form['quantity']
        remarks = request.form['remarks']
        user_id = session.get('user_id')

        new_request = RequestModel(user_id = session['user_id'] , item = item, quantity = int(quantity), remarks = remarks,)
        db.session.add(new_request)
        db.session.commit()
        
        show_alert = True
    
    return render_template('Emp_dash.html', role = 'employee', items = name_of_items,show_alert = show_alert )
#employee route end

#employee-view-requests
@app.route('/view-requests')
def view_employee_requests():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    
    user_id = session['user_id']
    my_requests= RequestModel.query.filter_by(user_id=user_id).order_by(RequestModel.date_requested.desc()).all()
    return render_template('emp_view_requests.html', requests = my_requests,role='employee')

#ad or head route
@app.context_processor
def inject_is_ad_or_head():
    user_id =  session.get('user_id')
    is_ad_or_head = False
    if user_id:
        is_ad_or_head = Department.query.filter(
            (Department.head_id == user_id) | (Department.ad_id == user_id)
        ).first() is not None
    return dict(is_ad_or_head=is_ad_or_head)

# monthly request for ad or head
@app.route('/ad/monthly-requests')
def ad_monthly_requests():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect('/login')
    user_id = session.get('user_id')
    # Get departments where user is AD or Head
    departments = Department.query.filter(
        (Department.head_id == user_id) | (Department.ad_id == user_id)
    ).all()
    department_ids = [d.id for d in departments]
    requests = (
        MonthlyRequest.query
        .join(User, MonthlyRequest.user_id == User.id)
        .filter(
            MonthlyRequest.department_id.in_(department_ids),
            User.role == 'admin'
        )
        .order_by(MonthlyRequest.date_requested.desc())
        .all()
    )
    return render_template('ad_monthly_requests.html', requests=requests, role=session.get('role'))
# ad or head action route
@app.route('/ad/monthly-request/<int:req_id>/action', methods=['POST'])
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
#ad request view route
@app.route('/ad/monthly-request/<int:req_id>')
def ad_view_monthly_request(req_id):
    if 'user_id' not in session:
        return redirect('/login')
    req = MonthlyRequest.query.get_or_404(req_id)
    return render_template('ad_monthly_request_view.html', req=req, user=req.user, role=session.get('role'))

if __name__=="__main__" :
    app.run(debug=True)