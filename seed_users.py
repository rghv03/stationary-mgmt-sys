from app import app,db
from models import User, Department
from werkzeug.security import generate_password_hash

def seed_users():

    procurement = Department.query.filter_by(shortname='Procurement').first()
    qrs_it = Department.query.filter_by(shortname='QRS & IT').first()
    research = Department.query.filter_by(shortname='Research').first()

    users = [
        User(
            username='superadmin',
            password = generate_password_hash('s123'),
            role='superadmin',
            department_id=qrs_it.id 
        ),
        User(
            username='admin1',
            password =generate_password_hash('a123'),
            role= 'admin',
            designation = 'Technical Officer',
            department_id = procurement.id
        ),
        User(
            username='admin2',
            password =generate_password_hash('a123'),
            role= 'admin',
            designation = 'Technical Officer',
            department_id = qrs_it.id
        ),
        User(
            username='emp1',
            password =generate_password_hash('e123'),
            role= 'employee',
            designation = 'Sc B',
            department_id = qrs_it.id
        ),
        User(
            username='emp2',
            password =generate_password_hash('e123'),
            role= 'employee',
            designation = 'Sc B',
            department_id =  research.id
        )
    ]
    
    db.session.add_all(users)
    db.session.commit()
    print("Users added Succesfully")
    

if __name__ == "__main__":
    with app.app_context():

        seed_users()
