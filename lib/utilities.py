from fbmq import QuickReply, Template
from model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from server import page
from settings import crafter, server_host
from datetime import timedelta, datetime

##############################################################################


def extract_data(event):
    """Exatract the information from message sent from Facebook."""
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
    """Handles adding a image S3 and image url to the database."""
    import boto3
    import requests
    s3 = boto3.resource('s3')
    image = Image(user_id=sender_id, url=image_url, created_at='now')
    db.session.add(image)
    db.session.commit()
    try:
        image_response = requests.get(image_url)
    except:
        pass
    else:
        s3.Bucket('acraftybot-test').put_object(Key="{}.jpg".format(image.image_id), Body=image_response.content) 
        image.url=' https://s3-us-west-2.amazonaws.com/acraftybot-test/{}.jpg'.format(image.image_id)
        db.session.commit()
    return image


def add_stock(stock_type, image):
    """Add either fabric or patttern stock to the database."""
    if stock_type == 'fabric':
        stock = Fabric(image_id=image.image_id, name="fabric", created_at='now')
    else:
        stock = Pattern(image_id=image.image_id, name="pattern", created_at='now')
    db.session.add(stock)
    db.session.commit()
    return stock


def add_stock_to_project(project_id, stock):
    """Connect stock to a particulare project based on project id."""
    project = Project.query.filter(Project.project_id == project_id).first()
    if isinstance(stock, Fabric):
        project.fabric_id = stock.fabric_id
    else:
        project.pattern_id = stock.pattern_id
    db.session.commit()
    return project


def add_project(sender_id, name):
    """Add a new project to the database"""
    new_project = Project(user_id=sender_id, name=name, created_at='now')
    db.session.add(new_project)
    db.session.commit()
    return new_project


def update_project_due_date(project_id, weeks):
    """Updates the project to have a due date within the database."""
    project = Project.query.filter(Project.project_id == project_id).first()
    project.due_at = project.created_at + timedelta(weeks=weeks)
    db.session.commit()
    return project


def update_project_notes(project_id, message_text):
    """Update the particulare project in the database with any user inputed notes."""
    project = Project.query.filter(Project.project_id == project_id).first()
    project.notes = message_text
    db.session.commit()
    return project


def add_user(sender_id):
    """Add a new user to the database."""
    user = User.query.filter(User.user_id == sender_id).first()
    if not user:
        user = User(user_id=sender_id)
        db.session.add(user)
        db.session.commit()
    return user


def add_next_stock_response(sender_id, stock_type):
    """If the user select an item from stock galleries retunr correct response."""
    if stock_type == 'pattern':
        if check_stock_count(stock_type='pattern', sender_id=sender_id) != 0:
            page.send(sender_id, Template.Buttons("If you have the material upload you next photo or pick something from your exisiting stock.", [{'type': 'web_url', 'title': 'Open Fabric Gallery', 'value': server_host + '/user/{}/fabric'.format(sender_id)}]))
        else:
            page.send(sender_id, "If you have the material upload you next photo")
    else:
        page.send(sender_id, "Success, How many weeks do you want to do this project?")


def add_status_update(project_id, image):
    """Update project status to the new status since a image was added."""
    project_count = db.session.query(db.func.count(Proj_Stat.proj_stat_id)).filter(Proj_Stat.project_id == project_id).first()[0]
    update_status = Proj_Stat(image_id=image.image_id, project_id=project_id, status_id=project_count+1, created_at='now')
    db.session.add(update_status)
    db.session.commit()
    return update_status


def check_stock_count(stock_type, sender_id):
    """Counts the number of items in stock."""

    if stock_type == 'fabric':
        fabric_count = Fabric.query.filter(Project.user_id == sender_id).all()
        return fabric_count.count()

    else:
        pattern_count = Pattern.query.filter(Project.user_id == sender_id).all()
        return pattern_count.count()


def delete_project(user_id, project_id):
    """Deletes a project from the database."""
    project = Project.query.filter(Project.project_id == project_id, Project.user_id == user_id).first()
    proj_stat = Proj_Stat.query.filter(Project.project_id == project_id).first()
    db.session.delete(proj_stat)
    db.session.delete(project)
    db.commit()


def delete_stock(user_id, stock_id, stock_type):
    """Deletes a project from the database."""
    if stock_type == 'fabric':
        fabric = Fabric.query.filter(Fabric.fabric_id == stock_id, Project.user_id == user_id).first()
        db.session.delete(fabric)
        db.commit()
    else:
        pattern = Pattern.query.filter(Pattern.pattern_id == stock_id, Project.user_id == user_id).first()
        db.session.delete(pattern)
        db.commit()
