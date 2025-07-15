from app import create_app
from extensions import db
from models import User, Department
from werkzeug.security import generate_password_hash
app = create_app()
def seed_users():

    procurement = Department.query.filter_by(shortname='Procurement').first()
    qrs_it = Department.query.filter_by(shortname='QRS & IT').first()
    
    users = [
        User(
            username='superadmin',
            password=generate_password_hash('super'),
            role='superadmin',
            first_name='Super',
            middle_name='',
            last_name='Admin',
            designation="Technical Officer 'B'",
            department_name=qrs_it.shortname
        ),
        User(
            username='admin1',
            password=generate_password_hash('admin'),
            role='admin',
            first_name='Admin',
            middle_name='',
            last_name='One',
            designation="Technical Officer 'B'",
            department_name=procurement.shortname
        ),
    ]
    User.query.delete()
    db.session.commit()
    print("All earlier users deleted")
    db.session.add_all(users)
    db.session.commit()
    print("Users added Succesfully")
    

if __name__ == "__main__":
    with app.app_context():

        seed_users()
