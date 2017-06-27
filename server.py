"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, redirect, request, flash, session


from model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

##############################################################################
# WIP

@page.handle_message
def received_message(event):
    sender_id = event.sender_id
    recipient_id = event.recipient_id
    time_of_message = event.timestamp
    message = event.message
    print("Received message for user %s and page %s at %s with message:"
          % (sender_id, recipient_id, time_of_message))
    print(message)

    seq = message.get("seq", 0)
    message_id = message.get("mid")
    app_id = message.get("app_id")
    metadata = message.get("metadata")

    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")

    if quick_reply:
        quick_reply_payload = quick_reply.get('payload')
        print("quick reply for message %s with payload %s" % (message_id, quick_reply_payload))

        page.send(sender_id, "Quick reply tapped")

    if message_text == "craftybot":
        craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Update Status", payload="UPDATE_STATUS")]
        page.send(sender_id,"How may I help you today?", quick_replies=craftybot, metadata="DEVELOPER_DEFINED_METADATA")

    elif message_attachments:
        image_type = [QuickReply( title="Fabric", payload="FABRIC"), QuickReply(title="Pattern", payload="PATTERN")]

        page.send(sender_id, "What is this an image of?", quick_replies=image_type, metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['NEW_PROJECT'])
def task_picker(payload, event):
    print (payload, event)
    sender_id = event.sender_id
    message = event.message_text
    page.send(sender_id, "Great. Please upload your first photo to start a new project", metadata="IMAGE_ONE")


@page.callback(['FABRIC'])
def callback_clicked_fabric(payload, event):
    """User selects fabric button"""
    sender_id = event.sender_id
    message = event.message_text
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "What do you know what you want to do with the fabric?", quick_replies=yes_no, metadata="DEVELOPER_DEFINED_METADATA")

@page.callback(['PATTERN'])
def callback_clicked_fabric(payload, event):
    """User selects pattern button"""
    sender_id = event.sender_id
    message = event.message_text
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Do you also have the fabric to make this pattern?", quick_replies=yes_no, metadata="DEVELOPER_DEFINED_METADATA")


@page.callback(['YES'])
def callback_clicked_fabric(payload, event):
    """User selects yes button"""
    sender_id = event.sender_id
    message = event.message_text
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Great. Please upload your next photo to add to the project", metadata="IMAGE_TWO")

@page.after_send
def after_send(payload, response):
    """:type payload: fbmq.Payload"""
    print "complete"


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")


##############################################################################


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
