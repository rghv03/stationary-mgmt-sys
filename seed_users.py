from app import app,db,User
from werkzeug.security import generate_password_hash

def seed_users():
    users = [
        User(
            username='superadmin',
            password = generate_password_hash('s123'),
            role='superadmin',
            department='QRS & IT' 
        ),
        User(
            username='admin1',
            password =generate_password_hash('a123'),
            role= 'admin',
            designation = 'Technical Officer',
            department = 'Procurement'
        ),
        User(
            username='emp1',
            password =generate_password_hash('e123'),
            role= 'employee',
            designation = 'Sc B',
            department = 'QRS & IT'
        )
    ]
    
    db.session.add_all(users)
    db.session.commit()
    print("Users added Succesfully")

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_users()
