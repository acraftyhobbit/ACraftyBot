from lib.utilities import total_inprogress, add_user, add_image, add_project, add_stock, add_stock_to_project, add_next_stock_response
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from fbmq import Page, Attachment, Template, QuickReply, NotificationType
from server import page
from settings import crafter, server_host
from datetime import timedelta, datetime

##############################################################################


def handle_message(event):
    """Handles all message types recieved by the bot and routes accordingly."""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    print message_text
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}

    if message_text and "craftybot" in message_text.lower(): #Lines 19 - 31 Handle all message dealing with text
        handle_start_route(sender_id=sender_id)

    elif message_text == 'New Project' or message_text == 'Add Stock' or message_text == 'Update Status' or message_text == 'Note'or message_text == 'No Notes':
        pass
    elif crafter[sender_id].get('current_route') == 'new_project' and not crafter[sender_id].get('project_id'):
        handle_project_name(sender_id=sender_id, message_text=message_text)

    elif crafter[sender_id].get('current_route') == 'new_project' and crafter[sender_id].get('fabric_id') and not crafter[sender_id].get('due_date'):
        handle_due_date(sender_id, message_text)

    elif crafter[sender_id].get('current_route') == 'new_project' and crafter[sender_id].get('due_date'):
        handle_project_notes(sender_id=sender_id, message_text=message_text)

    elif message_attachments: #Handles all message that are none text base, mostly attachmets
        image_url = message_attachments[0].get('payload', {}).get('url')
        if crafter[sender_id].get('current_route') == 'new_project' and crafter[sender_id].get('project_id') and not crafter[sender_id].get('fabric_id'):
            stock_type = 'pattern'
            if crafter[sender_id].get('pattern_id'):
                stock_type = 'fabric'
            handle_stock_image(sender_id=sender_id, image_url=image_url, stock_type=stock_type)

        elif crafter[sender_id].get('current_route') == 'add_stock':
            stock_type = crafter[sender_id].get('stock_type')
            handle_stock_image(sender_id=sender_id, image_url=image_url, stock_type=stock_type)

        elif crafter[sender_id].get('current_route') == 'update_status' and crafter[sender_id].get('project_id'):
            handle_status_image(sender_id=sender_id, image_url=image_url)


##############################################################################

def handle_start_route(sender_id):
    """Handles message text for first communication with bot."""
    user = add_user(sender_id=sender_id)
    total_inprogress(sender_id=sender_id)
    if total_inprogress(sender_id=sender_id) >= 6:
        craftybot = [QuickReply(title="Update Status", payload="UPDATE_STATUS"), QuickReply(title="Add Stock", payload="STOCK")]
        page.send(sender_id, "Sorry but you have reach maximum number of projects. You need to finish something before you can add another new project.", quick_replies=craftybot)
    else:
        craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Add Stock", payload="STOCK")]
        if total_inprogress(sender_id=sender_id) != 0:
            craftybot.append(QuickReply(title="Update Status", payload="UPDATE_STATUS"), )
        page.send(sender_id, "How may I help you today?", quick_replies=craftybot)


def handle_project_name(sender_id, message_text):
    """Handles message text for naming user's new project."""  # user can't call project project
    from lib.utilities import check_stock_count
    if message_text:
        project = add_project(sender_id=sender_id, name=message_text.strip())
        crafter[sender_id]['project_id'] = project.project_id
        if check_stock_count(stock_type='pattern', sender_id=sender_id) != 0:
            page.send(sender_id, Template.Buttons("Please upload your pattern photo to start a new project or click to open stock gallery.", [{'type': 'web_url', 'title': 'Open Stock Gallery', 'value': server_host + '/user/{}/pattern'.format(sender_id)}]))
        else:
            page.send(sender_id, "Please upload your pattern photo to start a new project")
    else:
        page.send(sender_id,"Sorry, didn't catch that.\nPlease add a project name")


def handle_stock_image(sender_id, image_url, stock_type):
    """Handles message attachment for user's pattern photo."""
    image = add_image(sender_id=sender_id, image_url=image_url)
    stock = add_stock(image=image, stock_type=stock_type)
    project_id = crafter[sender_id].get('project_id')
    crafter[sender_id][stock_type + '_id'] = getattr(stock, stock_type + '_id')
    if project_id:
        project = add_stock_to_project(stock=stock, project_id=project_id)
        add_next_stock_response(sender_id=sender_id, stock_type=stock_type)

    else:
        page.send(sender_id, Template.Buttons("This image has been add to your {} stock photos.To update a project say 'craftybot' or click to open your projects page".format(stock_type),[
            {'type': 'web_url', 'title': 'Open Projects Home', 'value': server_host + '/user/{}/projects'.format(sender_id)}]))
        crafter[sender_id] = dict()


def handle_due_date(sender_id, message_text):
    """Takes in the number of weeks a user has to do their new project."""
    from lib.utilities import update_project_due_date
    if message_text:
        try:
            weeks = int(message_text.strip())
        except:
            page.send(sender_id, "I'm sorry I didn't catch that.\nHow many weeks do you want to do this project?",)
        else:
            project_id = crafter[sender_id].get('project_id')
            project = update_project_due_date(project_id=project_id, weeks=weeks)
            note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTES")]
            page.send(sender_id, "Got it. Anything else you want me to know about this project", quick_replies=note_no)
            crafter[sender_id]['due_date'] = weeks
    else:
        page.send(sender_id,'Please add the number of weeks until you would like to work on this project')


def handle_project_notes(sender_id, message_text):
    """Handles any notes the user inputs to their new project."""
    from lib.utilities import update_project_notes
    if message_text:
        project_id = crafter[sender_id].get('project_id')
        project = update_project_notes(project_id=project_id, message_text=message_text)
        page.send(sender_id, Template.Buttons("Your note has been added to your project. If you would like to get back to main menu type 'craftybot' again or click to view your projects page.", [
            {'type': 'web_url', 'title': 'Open Projects Home', 'value': server_host + '/user/{}/projects'.format(sender_id)}]))
        crafter[sender_id] = dict()
    else:
        page.send(sender_id,'Did you want to leave a note?')


def handle_status_image(sender_id, image_url):
    """Handles message attachment for user's update photo."""
    from lib.utilities import add_status_update
    image = add_image(sender_id=sender_id, image_url=image_url)
    project_id = crafter[sender_id].get('project_id')
    update_status = add_status_update(project_id, image)

    project = Project.query.filter(Project.project_id == project_id).first()
    status = Status.query.filter(Status.status_id == update_status.status_id).first()
    due_date = datetime.strftime(project.due_at, "%A, %B %d, %Y")
    crafter[sender_id] = dict()
    page.send(sender_id, Template.Buttons("YAY! You're {status}. Just a reminder, this project is due by {due_date}. To update another project say 'craftybot'".format(status=status.name, due_date=due_date), [
            {'type': 'web_url', 'title': 'Open Projects Home', 'value': server_host + '/user/{}/projects'.format(sender_id)}]))
