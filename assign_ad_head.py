from app import app, db
from models import User, Department

with app.app_context():
    emp3 = User.query.filter_by(username='emp3').first()
    emp2 = User.query.filter_by(username='emp2').first()
    qrs_it = Department.query.filter_by(shortname='QRS & IT').first()
    research = Department.query.filter_by(shortname='Research').first()

    if qrs_it and emp3:
        qrs_it.ad_id = emp3.id
        print(f"Assigned {emp3.username} as AD of {qrs_it.shortname}")
    if research and emp2:
        research.head_id = emp2.id
        print(f"Assigned {emp2.username} as Head of {research.shortname}")

    db.session.commit()
    print("AD and Head assignment complete.")