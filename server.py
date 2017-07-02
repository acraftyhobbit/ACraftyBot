"""CraftyBot."""
import os
import sys
from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session
from fbmq import Page, Attachment, Template, QuickReply, NotificationType

from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from lib.utilities import extract_data, work_inprogress
from seed_status import create_status

app = Flask(__name__)
facebook = os.environ['FACEBOOK_TOKEN']
page = Page(facebook)
# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

app.jinja_env.undefined = StrictUndefined

##############################################################################
# WIP

user_state = {}
state = ['NEW_PROJECT', 'project_name', 'add_first_photo', 'add_type', 'yes_no', 'add_second_photo', 'due date', 'note', 'update_status', 'project_photo']
crafter = dict()


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        page.handle_webhook(request.get_data(as_text=True))
        return "ok"
    else:
        challenge = request.args.get('hub.challenge')
        return challenge


@page.handle_message
def received_message(event):
    from lib.message_handlers import handle_message
    handle_message(event=event)


@page.callback(['NEW_PROJECT'])
def task_new_project(payload, event):

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[0]
    page.send(sender_id, "Great. What would you like to call this project?")


@page.callback(['UPDATE_STATUS'])
def task_update_status(payload, event):

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[8]

    in_progress = work_inprogress(sender_id=sender_id)
    quick_replies = list()
    for name, project_id in in_progress:
        quick_replies.append(QuickReply(title=name, payload="project_{0}".format(project_id)))

    page.send(sender_id, "Great. Which project do you want to update?", quick_replies=quick_replies)


@page.callback(['project_(.+)'])
def select_project_callback(payload, event):
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    project_id = int(payload.split('_')[-1])
    crafter[sender_id]['project_id'] = project_id
    page.send(sender_id, "Upload you newest project photo.")


@page.callback(['FABRIC'])
def callback_clicked_fabric(payload, event):
    """User selects fabric button"""
    from lib.callbacks import fabric_callback_handler
    fabric_callback_handler(event=event)


@page.callback(['PATTERN'])
def callback_clicked_pattern(payload, event):
    """User selects pattern button"""
    from lib.callbacks import pattern_callback_handler
    pattern_callback_handler(event=event)


@page.callback(['YES'])
def callback_clicked_yes(payload, event):
    """User selects yes button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[4]
    page.send(sender_id, "Great. Please upload your next photo to add to the project")


@page.callback(['NOTE'])
def callback_clicked_note(payload, event):
    """User selects nopte button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[7]
    page.send(sender_id, "Please tell me the notes about this project")


@app.route("/projects")
def all_projects():
    """Show list of projects."""
    project_dicts = list()
    projects = Project.query.order_by(Project.project_id).all()
    for project in projects:
        project_dict = dict(
            project_id=project.project_id,
            name=project.name,
            fabric_image=project.fabric.image.url,
            pattern_image=project.pattern.image.url,
            status_images=[stat.image.url for stat in project.proj_stat]
            )
        project_dicts.append(project_dict)
    return render_template("projects.html", projects=project_dicts)


@app.route("/projects/<project_id>")
def project_details(project_id):
    """Show project details."""

    project = Project.query.filter_by(project_id=project_id).one()
    return render_template("project-details.html", project=project)


@page.after_send
def after_send(payload, response):
    """:type payload: fbmq.Payload"""
    print "complete"

##############################################################################


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # Use the DebugToolbar
    # DebugToolbarExtension(app)
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()
    status = Status.query.all()
    if not status:
        create_status()

    app.run(host="0.0.0.0")
