from fbmq import QuickReply
from lib.utilities import extract_data
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from server import page, user, user_state, state


##############################################################################

def fabric_callback_handler(event):
    """Handles fabric callback function."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[3]
    image_id = user[sender_id].get('image_id')
    image_type = Fabric(image_id=image_id, name=quick_reply)
    db.session.add(image_type)
    db.session.commit()
    fabric_id = Fabric.query.filer(image_id=image_id).one()
    user[sender_id]['type_id'] = fabric_id.fabric_id
    project_id = user[sender_id].get('project_id')
    update = Project.query.filter(Project.project_id == project_id)
    update.fabric_id = user[sender_id].get('type_id')
    #supply = dict() create a new supply object with the image_url, user_id etc.
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Do you know what you want to do with the fabric?", quick_replies=yes_no, metadata="supply.id")
