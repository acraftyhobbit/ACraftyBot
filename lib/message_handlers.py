from lib.utilities import extract_data, total_inprogress
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from fbmq import Page, Attachment, Template, QuickReply, NotificationType
from server import user_state, state, page, crafter
from datetime import timedelta, datetime

##############################################################################


def handle_message(event):
    """Handles message types recieved by the bot."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)

    if message_text and "craftybot" in message_text.lower():
        handle_text_event_1(event=event)

    elif message_text and user_state.get(sender_id) == state[0]:
        handle_text_event_2(event=event)

    elif message_text and user_state.get(sender_id) == state[5]:
        try:
            weeks = int(message_text.strip())
        except:
            page.send(sender_id, "I'm sorry I didn't catch that.\nHow many weeks do you want to do this project?",)
        else:
            user_state[sender_id] = state[6]
            project_id = crafter[sender_id].get('project_id')
            project = Project.query.filter(Project.project_id == project_id).first()
            project.due_at = project.created_at + timedelta(weeks=weeks)
            db.session.commit()
            note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTE")]
            page.send(sender_id, "Got it. Anything else you want me to know about this project", quick_replies=note_no, metadata="Due_Date")

    elif message_text and user_state.get(sender_id) == state[7]:
        user_state[sender_id] = state[0]
        project_id = crafter[sender_id].get('project_id')
        project = Project.query.filter(Project.project_id == project_id).first()
        project.notes = message_text
        db.session.commit()
        page.send(sender_id, "Your note has been added to your project. If you would like to get back to main menu type 'craftybot' again.")

    elif message_attachments and user_state.get(sender_id) == state[1]:
        handle_image_event_1(event=event)

    elif message_attachments and user_state.get(sender_id) == state[4]:
        handle_image_event_2(event=event)

    elif message_attachments and user_state.get(sender_id) == state[8]:
        handle_image_event_3(event=event)


##############################################################################

def handle_text_event_1(event):
    """Handles message text for first communication with bot."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    new_user = User.query.filter(User.user_id == sender_id).all()
    crafter[sender_id] = {}
    if not new_user:
        user = User(user_id=sender_id)
        db.session.add(user)
        db.session.commit()
    total_inprogress(sender_id=sender_id)


def handle_text_event_2(event):
    """Handles message text for naming user's new project."""  # user can't call project project
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[1]
    new_project = Project(user_id=sender_id, name=message_text, created_at='now')
    db.session.add(new_project)
    db.session.commit()
    project_id = Project.query.filter(Project.name == message_text, Project.user_id == sender_id).first()
    crafter[sender_id]['project_id'] = project_id.project_id  # can I also pull name to make text say name
    page.send(sender_id, "Please upload your first photo to start a new project")


def handle_image_event_1(event):
    """Handles message attachment for user's 1st photo."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[2]
    first_image = Image(user_id=sender_id, url=message_attachments[0].get('payload').get('url'), created_at='now')
    db.session.add(first_image)
    db.session.commit()
    crafter[sender_id]['1st_image_id'] = first_image.image_id
    image_type = [QuickReply(title="Fabric", payload="FABRIC"), QuickReply(title="Pattern", payload="PATTERN")]
    page.send(sender_id, "What is this an image of?", quick_replies=image_type)


def handle_image_event_2(event):
    """Handles message attachment for user's 2nd photo."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[5]
    second_image = Image(user_id=sender_id, url=message_attachments[0].get('payload', {}).get('url'), created_at='now')
    db.session.add(second_image)
    project_id = crafter[sender_id].get('project_id')
    db.session.commit()

    if crafter[sender_id].get('pattern_id'):
        fabric = Fabric(image_id=second_image.image_id, name='fabric', created_at='now')
        db.session.add(fabric)
        project_id = crafter[sender_id].get('project_id')
        project = Project.query.filter(Project.project_id == project_id).first()
        project.fabric_id = fabric.fabric_id
        db.session.commit()
    elif crafter[sender_id].get('fabric_id'):
        pattern = Pattern(image_id=second_image.image_id, name="pattern", created_at='now')
        db.session.add(pattern)
        project_id = crafter[sender_id].get('project_id')
        project = Project.query.filter(Project.project_id == project_id).first()
        project.pattern_id = pattern.pattern_id
        db.session.commit()
    page.send(sender_id, "Success, How many weeks do you want to do this project?")


def handle_image_event_3(event):
    """Handles message attachment for user's 1st photo."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = None
    update_image = Image(user_id=sender_id, url=message_attachments[0].get('payload').get('url'), created_at='now')
    db.session.add(update_image)
    project_id = crafter[sender_id].get('project_id')
    project_count = db.session.query(db.func.count(Proj_Stat.proj_stat_id)).filter(Proj_Stat.project_id == project_id).first()[0]
    update_stat = Proj_Stat(image_id=update_image.image_id, project_id=project_id, status_id=project_count+1, created_at='now')
    db.session.add(update_stat)
    db.session.commit()

    project = Project.query.filter(Project.project_id == project_id).first()
    status = Status.query.filter(Status.status_id == update_stat.status_id).first()
    due_date = datetime.strftime(project.due_at, "%A, %B %d, %Y")

    page.send(sender_id, "YAY! You're {status}. Reminder your due date is {due_date}. To update another project say 'craftybot'".format(status=status.name, due_date=due_date))
