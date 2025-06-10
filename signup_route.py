from flask import Blueprint,render_template,request,redirect
from werkzeug.security import generate_password_hash
from models import db,User

signup_bp = Blueprint('signup',__name__)

@signup_bp.route('/signup',methods =['GET','POST'])
def signup():
    error = None
    show_alert = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        designation = request.form['designation']
        department = request.form['department']

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
            user = User(username=username,password=hashed_pw, role = 'employee',
                        designation=designation, department=department)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
    return render_template('signup.html', error = error,show_alert = show_alert )

