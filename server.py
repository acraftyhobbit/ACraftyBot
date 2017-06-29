"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session
from fbmq import Page, Attachment, Template, QuickReply, NotificationType

from model import connect_to_db, db


app = Flask(__name__)
page = Page()
# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

##############################################################################
# WIP

user_state = {}

state = ['NEW_PROJECT', 'project_name', 'add_first_photo', 'add_type', 'yes_no', 'add_second_photo', 'due date', 'note', ]


def extract_data(event):
    sender_id = event.sender_id
    time_of_message = event.timestamp
    message = event.message
    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")
    #payload = quick_reply.get('payload')

    return sender_id, message, message_text, message_attachments, quick_reply


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

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)

    if message_text and "craftybot" in message_text.lower():

        craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Update Status", payload="UPDATE_STATUS")]
        new_user = User.query.filter(user_id=sender_id).all
        if not new_user:
            user = User(user_id=sender_id)
            db.sesssion.add(user)
            db.sesssion.commit()
        page.send(sender_id, "How may I help you today?", quick_replies=craftybot, metadata='now it is a string')

    elif message_text and user_state.get(sender_id) == state[0]:
        user_state[sender_id] = state[1]

        page.send(sender_id, "Please upload your first photo to start a new project", metadata="IMAGE_ONE")

    elif message_text and user_state.get(sender_id) == state[5]:
        user_state[sender_id] = state[6]
        note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTE")]
        page.send(sender_id, "Got it. Anything else you want me to know about this project", metadata="Due_Date")

    elif message_attachments and user_state.get(sender_id) == state[1]:
        image_id = 1  # add to db
        user_state[sender_id] = state[2]
        image_type = [QuickReply(title="Fabric", payload="FABRIC"), QuickReply(title="Pattern", payload="PATTERN")]
        page.send(sender_id, "What is this an image of?", quick_replies=image_type, metadata="message_attachments")

    elif message_attachments and user_state.get(sender_id) == state[4]:
        user_state[sender_id] = state[5]
        page.send(sender_id, "Success, How many weeks do you want to do this project?",)


@page.callback(['NEW_PROJECT'])
def task_picker(payload, event):

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    user_state[sender_id] = state[0]
    page.send(sender_id, "Great. What would you like to call this project?", metadata="project_name")


@page.callback(['FABRIC'])
def callback_clicked_fabric(payload, event):
    """User selects fabric button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    image_id = payload.split('__')[-1]
    user_state[sender_id] = state[3]
    supply = dict()  # create a new supply object with the image_url, user_id etc.
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Do you know what you want to do with the fabric?", quick_replies=yes_no, metadata="supply.id")


@page.callback(['PATTERN'])
def callback_clicked_pattern(payload, event):
    """User selects pattern button"""

    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Do you also have the fabric to make this pattern?", quick_replies=yes_no, metadata="DEVELOPER_DEFINED_METADATA")


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

    app.run(host="0.0.0.0")
