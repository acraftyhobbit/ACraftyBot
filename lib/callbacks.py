from fbmq import QuickReply
from lib.utilities import extract_data
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from server import page, crafter, user_state, state


##############################################################################

def fabric_callback_handler(event):
    """Handles fabric callback function."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id in crafter.keys():
        user_state[sender_id] = state[3]
        image_id = crafter[sender_id].get('1st_image_id')
        fabric = Fabric(image_id=image_id, name="fabric", created_at='now')
        db.session.add(fabric)
        project_id = crafter[sender_id].get('project_id')
        project = Project.query.filter(Project.project_id == project_id).first()
        project.fabric_id = fabric.fabric_id
        db.session.commit()
        crafter[sender_id]['fabric_id'] = fabric.fabric_id
        yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
        page.send(sender_id, "Do you know what you want to do with the fabric?", quick_replies=yes_no, metadata="supply.id")


def pattern_callback_handler(event):
    """Handles pattern callback function."""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id in crafter.keys():
        user_state[sender_id] = state[3]
        image_id = crafter[sender_id].get('1st_image_id')
        pattern = Pattern(image_id=image_id, name="pattern", created_at='now')
        db.session.add(pattern)
        project_id = crafter[sender_id].get('project_id')
        project = Project.query.filter(Project.project_id == project_id).first()
        project.pattern_id = pattern.pattern_id
        db.session.commit()
        crafter[sender_id]['pattern_id'] = pattern.pattern_id
        yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
        page.send(sender_id, "Do you also have the fabric to make this pattern?", quick_replies=yes_no, metadata="supply")
