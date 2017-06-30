from lib.utilities import extract_data
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from fbmq import Page, Attachment, Template, QuickReply, NotificationType
from server import user_state, state, page, user

##############################################################################


def handle_message(event):
    """Handles message types recieved by the bot."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if message_text and "craftybot" in message_text.lower():
        handle_text_event_1(event=event)

    elif message_text and user_state.get(sender_id) == state[0]:
        handle_text_event_2(event=event)

    elif message_text and user_state.get(sender_id) == state[5]:
        user_state[sender_id] = state[6]
        note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTE")]
        page.send(sender_id, "Got it. Anything else you want me to know about this project", quick_replies=note_no, metadata="Due_Date")

    elif message_attachments and user_state.get(sender_id) == state[1]:
        handle_text_image_1(event=event)

    elif message_attachments and user_state.get(sender_id) == state[4]:
        user_state[sender_id] = state[5]
        page.send(sender_id, "Success, How many weeks do you want to do this project?",)


##############################################################################

def handle_text_event_1(event):
    """Handles message text for first communication with bot."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)

    new_user = User.query.filter(User.user_id == sender_id).all()
    if not new_user:
        user = User(user_id=sender_id)
        db.session.add(user)
        db.session.commit()

    craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Update Status", payload="UPDATE_STATUS")]
    page.send(sender_id, "How may I help you today?", quick_replies=craftybot, metadata='now it is a string')


def handle_text_event_2(event):
    """Handles message text for naming user's new project."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[1]
    new_project = Project(user_id=sender_id, name=message_text, created_at='now')
    db.session.add(new_project)
    db.session.commit()

    project_id = Project.query.filter(Project.name == message_text, user_id=sender_id).first()
    user[sender_id]['project_id'] = project_id.project_id  # can I also pull name to make text say name
    page.send(sender_id, "Please upload your first photo to start a new project", metadata="IMAGE_ONE")


def handle_image_event_1(event):
    """Handles message attachment for user's 1st photo."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[2]
    first_image = Image(user_id=sender_id, url=message_attachments[0].get('payload').get('url'))
    db.session.add(first_image)
    db.session.commit()

    image_id = Image.query.filter(Image.url == message_attachments[0].get('payload').get('url'))
    user[sender_id]['1st_image_id'] = image_id.image_id
    image_type = [QuickReply(title="Fabric", payload="FABRIC"), QuickReply(title="Pattern", payload="PATTERN")]
    page.send(sender_id, "What is this an image of?", quick_replies=image_type, metadata="message_attachments")
