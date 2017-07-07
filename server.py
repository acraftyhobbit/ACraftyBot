"""CraftyBot."""
import os
import sys
from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session
from fbmq import Page, Attachment, Template, QuickReply, NotificationType

from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from lib.utilities import extract_data, work_inprogress
from seed_status import create_status
from datetime import datetime

app = Flask(__name__)
facebook = os.environ['FACEBOOK_TOKEN']
page = Page(facebook)
# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

app.jinja_env.undefined = StrictUndefined

##############################################################################


user_state = {}
state = ['NEW_PROJECT', 'project_name', 'add_first_photo', 'add_type', 'yes_no', 'add_second_photo', 'due date', 'note', 'update_status', 'project_photo', 'update_stock', 'fabric_stock', 'pattern_stock']
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


@page.callback(['NEW_STOCK'])
def task_new_stock(payload, event):

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[10]
    stock_type = [QuickReply(title="Fabric Stock", payload="FABRIC_STOCK"), QuickReply(title="Pattern Stock", payload="PATTERN_STOCK")]
    page.send(sender_id, "Great. Which stock do you want to update?", quick_replies=stock_type)


@page.callback(['FABRIC_STOCK'])
def callback_clicked_fabric_stock(payload, event):
    """User selects fabric button"""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[11]
    page.send(sender_id, "Upload your photo of the fabric you want to add to stock.")


@page.callback(['PATTERN_STOCK'])
def callback_clicked_pattern_stock(payload, event):
    """User selects fabric button"""
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[12]
    page.send(sender_id, "Upload your photo of the pattern you want to add to stock.")


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

@page.callback(['NO'])
def callback_clicked_no(payload, event):
    """User selects no button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[4]
    page.send(sender_id, Template.Buttons("Do you want to use something from  your stock?",[
        {'type': 'web_url', 'title': 'Open Stock Gallery', 'value': 'http://localhost:5000/{0}/fabric-gallery'.format(sender_id)}]))


@page.callback(['NOTE'])
def callback_clicked_note(payload, event):
    """User selects note button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[7]
    page.send(sender_id, "Please tell me the notes about this project")


@page.callback(['NO_NOTES'])
def callback_clicked_no_note(payload, event):
    """User selects no note button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = None
    page.send(sender_id, "Your project has been saved. If you would like to get back to main menu type 'craftybot' again.")


@app.route("/<user_id>/projects")
def all_projects():
    """Show list of projects."""
    project_dicts = list()
    projects = Project.query.filter(Project.fabric_id != None, Project.pattern_id != None).order_by(Project.project_id).all()
    for project in projects:
        project_dict = dict(
            project_id=project.project_id,
            name=project.name,
            fabric_image=project.fabric.image.url,
            pattern_image=project.pattern.image.url,
            due_at=datetime.strftime(project.due_at, "%Y-%m-%d"),
            status_images=[stat.image.url for stat in project.proj_stat])
        project_dicts.append(project_dict)
    return render_template("projects.html", projects=project_dicts)


@app.route("/projects/<project_id>")
def project_details(project_id):
    """Show project details."""

    project = Project.query.filter_by(project_id=project_id).one()
    due_at = datetime.strftime(project.due_at, "%A, %B %d, %Y")
    return render_template("project-details.html", project=project, due_at=due_at)


@app.route("/fabric-gallery")
def fabric_stock_gallery():
    """Show all fabric images."""
    sender_id = 1397850150328689
    fabrics = db.session.query(Fabric.fabric_id, Image.url).join(Image).filter(Image.user_id == sender_id).all()
    return render_template("fabric_gallery.html", fabrics=fabrics)


@app.route("/pattern-gallery")
def pattern_stock_gallery():
    """Show all fabric images."""
    sender_id = 1397850150328689
    patterns = db.session.query(Pattern.pattern_id, Image.url).join(Image).filter(Image.user_id == sender_id).all()
    return render_template("pattern-gallery.html", patterns=patterns)


@app.route("/add-to-favorites", methods=["POST"])
def add_to_favorites():
    stock_id = request.form.get("id")
    stock_type = request.form.get('stock_type')
    user_id = request.form.get("user_id")
    project_id = session.get(user_id, dict()).get('project_id')
    'https://www.craftbot.com/user/1397850150328689/fabric'

    if stock_type == 'fabric':
        project = Project.query.filter(Project.project_id == project_id).first()
        project.fabric_id = stock_id
        db.session.commit()
    # put this in a "favorites" table?

    response = { 'status': "success", 'id': photo_id }
    return jsonify(response)


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
