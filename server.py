"""CraftyBot."""
import os
from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session
from fbmq import Page, Attachment, Template, QuickReply, NotificationType

from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from lib.utilities import extract_data

app = Flask(__name__)
page = Page(os.environ['FACEBOOK_TOKEN'])
# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

app.jinja_env.undefined = StrictUndefined

##############################################################################
# WIP

user_state = {}
state = ['NEW_PROJECT', 'project_name', 'add_first_photo', 'add_type', 'yes_no', 'add_second_photo', 'due date', 'note', ]
cheesecake = dict()


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
def task_picker(payload, event):

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[0]
    page.send(sender_id, "Great. What would you like to call this project?", metadata="project_name")


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
    page.send(sender_id, "Great. Please upload your next photo to add to the project", metadata="IMAGE_TWO")

@page.callback(['NOTE'])
def callback_clicked_note(payload, event):
    """User selects nopte button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[7]
    page.send(sender_id, "Please tell me the notes about this project", metadata="notes")

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

    app.run(host="0.0.0.0")