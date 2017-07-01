#status table
from lib.model import Status, db

def create_status():
    """Creates Status Table Rows"""
    status_1 = Status(name="Cut Out pattern pieces from fabric",)
    status_2 = Status(name="25% Complete",)
    status_3 = Status(name="50% Complete",)
    status_4 = Status(name="75% Complete",)
    status_5 = Status(name="Finishing Touches",)
    status_6 = Status(name="Completed Project",)
    db.session.add(status_1)
    db.session.add(status_2)
    db.session.add(status_3)
    db.session.add(status_4)
    db.session.add(status_5)
    db.session.add(status_6)
    db.session.commit()


 # INSERT INTO status (name) VALUES ('Cut Out pattern pieces from fabric'), ('25% Complete'), ('50% Complete'), ('75% Complete'), ('Finishing Touches'), ('Completed Project');
