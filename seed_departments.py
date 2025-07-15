from app import create_app
from extensions import db
from models import Department
app = create_app()

departments = [
    {"shortname": "Procurement"},
    {"shortname": "QRS & IT"},
    {"shortname": "Research"},
    {"shortname": "MMG"}
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for dept in departments:
        d = Department(shortname=dept["shortname"])
        db.session.add(d)
    db.session.commit()
    print("Departments seeded successfully")
