from lib.utilities import extract_data, total_inprogress
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from fbmq import Page, Attachment, Template, QuickReply, NotificationType
from server import user_state, state, page, crafter
from datetime import timedelta, datetime

##############################################################################


def handle_message(event):
    """Handles message types recieved by the bot."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)

    if not crafter[sender_id].get('current_route'):
        handle_start_route(sender_id=sender_id)

    elif crafter[sender_id]['current_route'] == 'new_project' and not crafter[sender_id].get('project_id') :
        handle_project_name(sender_id=sender_id, message_text=message_text)

    elif crafter[sender_id]['current_route'] == 'new_project' and crafter[sender_id].get('fabric_id') and not crafter[sender_id].get('due_date'):
        handle_due_date(sender_id, message_text)

    elif crafter[sender_id]['current_route'] == 'new_project' and crafter[sender_id].get('due_date'):
        handle_project_notes(sender_id=sender_id, message_text=message_text)

    elif message_attachments:
        image_url = message_attachments[0].get('payload', {}).get('url')
        if crafter[sender_id]['current_route'] == 'new_project' and crafter[sender_id].get('project_id') and not crafter[sender_id].get('fabric_id'):
            stock_type = 'pattern'
            if crafter[sender_id].get('pattern_id'):
                stock_type = 'fabric'
            handle_stock_image(sender_id=sender_id, image_url=image_url, stock_type=stock_type)

        elif crafter[sender_id]['current_route'] == 'add_stock':
            stock_type = crafter[sender_id].get('stock_type')
            handle_stock_image(sender_id=sender_id, image_url=image_url, stock_type=stock_type)

        elif crafter[sender_id]['current_route'] == 'update_status' and crafter[sender_id].get('project_id'):
            handle_status_image(sender_id=sender_id, image_url=image_url)


##############################################################################

def handle_start_route(sender_id):
    """Handles message text for first communication with bot."""
    user = add_user(sender_id=sender_id)
    crafter[sender_id] = {}
    total_inprogress(sender_id=sender_id)

    if total_inprogress >= 6:
        craftybot = [QuickReply(title="Update Status", payload="UPDATE_STATUS"), QuickReply(title="Add Stock", payload="NEW_STOCK")]
        page.send(sender_id, "You have reach max for projects. You need to finish something before you can add another new project.", quick_replies=craftybot)
    else:
        craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Add Stock", payload="NEW_STOCK")]

        if total_inprogress !=0:
            craftybot.append(QuickReply(title="Update Status", payload="UPDATE_STATUS"), )
        page.send(sender_id, "How may I help you today?", quick_replies=craftybot)


def handle_project_name(sender_id, message_text):
    """Handles message text for naming user's new project."""  # user can't call project project
    if message_text:
        project = add_project(sender_id=sender_id, name=message_text.strip())
        crafter[sender_id]['project_id'] = project.project_id
        page.send(sender_id, Template.Buttons("Please upload your pattern photo to start a new project or click to open stock gallery.",[
            {'type': 'web_url', 'title': 'Open Stock Gallery', 'value': 'http://localhost:5000/pattern-gallery'}]))
    else:
        page.send('please add a project name')

def handle_stock_image(sender_id, image_url, stock_type):
    """Handles message attachment for user's pattern photo."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    image = add_image(sender_id=sender_id, image_url=image_url)
    stock = add_stock(image=image, stock_type=stock_type)
    project_id = crafter[sender_id].get('project_id')
    crafter[sender_id][stock_type + '_id'] = getattr(stock, stock_type + '_id')
    if project_id:
        project = add_stock_to_project(stock=stock, project_id=project_id)
        add_next_stock_response(sender_id=sender_id, stock_type=stock_type)

    else:
        page.send(sender_id, "This image has been add to your {0} stock photos.To update another project say 'craftybot'".format(stock_type))


def handle_due_date(sender_id, message_text):
    try:
        weeks = int(message_text.strip())
    except:
        page.send(sender_id, "I'm sorry I didn't catch that.\nHow many weeks do you want to do this project?",)
    else:
        crafter[sender_id]['due_date'] = weeks
        project_id = crafter[sender_id].get('project_id')
        project = add_project_due_date(project_id=project_id, weeks=weeks)
        note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTES")]
        page.send(sender_id, "Got it. Anything else you want me to know about this project", quick_replies=note_no)


def handle_project_notes(sender_id, message_text):
    if message_text:
        project_id = crafter[sender_id].get('project_id')
        project = update_project_notes(project_id=project_id, message_text=message_text)
        page.send(sender_id, "Your note has been added to your project. If you would like to get back to main menu type 'craftybot' again.")
        crafter[sender_id] = dict()
    else:
        page.send('did you want to leave a note?')


def handle_status_image(event):
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