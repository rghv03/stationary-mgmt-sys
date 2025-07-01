from app import app,db
from models import Department

departments = [
    {"shortname": "Procurement"},
    {"shortname": "QRS & IT"},
    {"shortname": "Research"},
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for dept in departments:
        d = Department(shortname=dept["shortname"])
        db.session.add(d)
    db.session.commit()
    print("Departments seeded successfully")
