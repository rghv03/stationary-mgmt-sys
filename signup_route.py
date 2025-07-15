from flask import Blueprint,render_template,request,redirect
from werkzeug.security import generate_password_hash
from models import db,User,Department

signup_bp = Blueprint('signup',__name__)

DESIGNATIONS = [
    "Technical Officer 'B'",
    "Scientist 'B'",
    "Scientist 'C'",
    "Scientist 'D'",
    "Scientist 'E'",
    "Scientist 'F'",
    "Scientist 'G'"
]

@signup_bp.route('/signup',methods =['GET','POST'])
def signup():
    error = None
    show_alert = False
    departments = Department.query.all()  
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name','')
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        designation = request.form['designation']
        department_name = request.form['department_name']


        existing_user = User.query.filter_by(username=username).first()
        admin_exists = User.query.filter_by(role='admin').first()
        superadmin_exists = User.query.filter_by(role='superadmin').first()

        if password != confirm_password:
            show_alert = True
        elif existing_user:
            error = "Username already exists."
        elif not admin_exists or not superadmin_exists:
            error = "Signup disabled until both admin and superadmin are created "
        else:
            hashed_pw = generate_password_hash(password)
            user = User(first_name=first_name,middle_name=middle_name,last_name=last_name,username=username,password=hashed_pw, role ='employee',
                        designation=designation, department_name=department_name)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('signup.html', error = error,show_alert = show_alert, departments=departments,designations=DESIGNATIONS)

