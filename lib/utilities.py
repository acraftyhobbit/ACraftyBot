
def extract_data(event):
    sender_id = event.sender_id
    message = event.message
    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    return sender_id, message, message_text, message_attachments, quick_reply


def total_inprogress(sender_id):
    """Counts the number of inprogess projects in queue."""
    from lib.model import Project, Proj_Stat, db
    from fbmq import QuickReply
    from server import page

    complete = db.session.query(db.func.count(Project.project_id)).join(Proj_Stat).filter(Project.user_id == sender_id, Proj_Stat.status_id == 6).all()

    project_count = db.session.query(db.func.count(Project.project_id)).filter(Project.user_id == sender_id).all()

    total_inprogress = project_count[0][0] - complete[0][0]
    print(total_inprogress)
    if total_inprogress >= 6:
        craftybot = [QuickReply(title="Update Status", payload="UPDATE_STATUS")]
        page.send(sender_id, "You have reach max for projects. You need to finish something before you can another new project.", quick_replies=craftybot, metadata='now it is a string')
    else:
        craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Update Status", payload="UPDATE_STATUS")]
        page.send(sender_id, "How may I help you today?", quick_replies=craftybot, metadata='now it is a string')


def work_inprogress(sender_id):
    """Pull all projects that are not complete"""
    from lib.model import Project, Proj_Stat, db

    complete = db.session.query(Project.project_id).join(Proj_Stat).filter(Project.user_id == sender_id, Proj_Stat.status_id == 6).all()

    if not complete:

        inprogress = db.session.query(Project.name, Project.project_id).filter(Project.user_id == sender_id).all()
    else:
        inprogress = db.session.query(Project.name, Project.project_id).filter(db.not_(Project.project_id.in_(complete))) & (Project.user_id == sender_id).all()
    return inprogress
