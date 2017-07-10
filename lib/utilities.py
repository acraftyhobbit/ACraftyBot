from fbmq import QuickReply
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from server import page
from settings import crafter
from datetime import timedelta, datetime

##############################################################################


def extract_data(event):
    sender_id = event.sender_id
    message = event.message
    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    return sender_id, message, message_text, message_attachments, quick_reply


def total_inprogress(sender_id):
    """Counts the number of inprogess projects in queue."""

    complete = db.session.query(db.func.count(Project.project_id)).join(Proj_Stat).filter(Project.user_id == sender_id, Proj_Stat.status_id == 6).all()

    project_count = db.session.query(db.func.count(Project.project_id)).filter(Project.user_id == sender_id).all()

    total_projects = project_count[0][0] - complete[0][0]
    return total_projects


def work_inprogress(sender_id):
    """Pull all projects that are not complete"""

    complete = db.session.query(Project.project_id).join(Proj_Stat).filter(Project.user_id == sender_id, Proj_Stat.status_id == 6).all()

    if not complete:

        inprogress = db.session.query(Project.name, Project.project_id, Project.due_at).filter(Project.user_id == sender_id).all()
    else:
        inprogress = db.session.query(Project.name, Project.project_id, Project.due_at).filter(db.not_(Project.project_id.in_(complete)) & (Project.user_id == sender_id)).all()
    return inprogress


def add_image(sender_id, image_url):
    image = Image(user_id=sender_id, url=image_url, created_at='now')
    db.session.add(image)
    db.session.commit()
    return image


def add_stock(stock_type, image):
    if stock_type == 'fabric':
        stock = Fabric(image_id=image.image_id, name="fabric", created_at='now')
    else:
        stock = Pattern(image_id=image.image_id, name="pattern", created_at='now')
    db.session.add(stock)
    db.session.commit()
    return stock


def add_stock_to_project(project_id, stock):
    project = Project.query.filter(Project.project_id == project_id).first()
    if isinstance(stock, Fabric):
        project.fabric_id = stock.fabric_id
    else:
        project.pattern_id = stock.pattern_id
    db.session.commit()
    return project


def add_project(sender_id, name):
    new_project = Project(user_id=sender_id, name=name, created_at='now')
    db.session.add(new_project)
    db.session.commit()
    return new_project


def update_project_due_date(project_id, weeks):
    project = Project.query.filter(Project.project_id == project_id).first()
    project.due_at = project.created_at + timedelta(weeks=weeks)
    db.session.commit()
    return project


def update_project_notes(project_id, message_text):
    project = Project.query.filter(Project.project_id == project_id).first()
    project.notes = message_text
    db.session.commit()
    return project


def add_user(sender_id):
    user = User.query.filter(User.user_id == sender_id).first()
    if not user:
        user = User(user_id=sender_id)
        db.session.add(user)
        db.session.commit()
    return user


def add_next_stock_response(sender_id, stock_type):
    if stock_type == 'pattern':
        yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
        page.send(sender_id, "Got it! Do you have the fabric you want to make this pattern with?", quick_replies=yes_no)
    else:
        page.send(sender_id, "Success, How many weeks do you want to do this project?")


def add_status_update(project_id, image):
    project_count = db.session.query(db.func.count(Proj_Stat.proj_stat_id)).filter(Proj_Stat.project_id == project_id).first()[0]
    update_status = Proj_Stat(image_id=image.image_id, project_id=project_id, status_id=project_count+1, created_at='now')
    db.session.add(update_status)
    db.session.commit()
    return update_status

