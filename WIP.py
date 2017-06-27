
from flask import Flask, request
from fbmq import Page, Attachment, Template, QuickReply
app = Flask(__name__)
page = Page()


@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text
    craftybot = [QuickReply(title="New Project", payload="new_project"), QuickReply(title="Update Status", payload="update_status")]

    page.send(recipient_id,
              "How may I help you today?",
              quick_replies=quick_replies,
              metadata="DEVELOPER_DEFINED_METADATA")


@page.handle_postback('new_project')
def new_project():

    page.send(reciept_id, "Great. Please upload your first photo to start a new project",)


@page.handle_postback()
def firstimg_handler(event):
    """1st project photo handler."""
    sender_id = event.sender_id
    message = event.message.get('attachments')
    type_buttons = [Templates.ButtonPostBack("Fabric", "Fabric_payload"), Templates.ButtonPostBack("Pattern", "Pattern_payload")]

    page.send(reciept_id, "What is this an image of?", type_buttons)


@page.handle_postback(['DEVELOPED_DEFINED_PAYLOAD'])
def fabric_button_click(payload, event):
    """User selects fabric button"""

    page.send(reciept_id, "What do you know what you want to do with the fabric?",)


@page.handle_postback(['DEVELOPED_DEFINED_PAYLOAD'])
def pattern_button_click(payload, event):
    """User selects Pattern button"""

    page.send(reciept_id, "Do you also have the fabric to make this pattern?",)


@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    page.send(sender_id, 'Great. Please upload a photo of that too.')


@page.handle_message()
def second_img_handler(event):
    """1st project photo handler."""
    sender_id = event.sender_id
    message = event.message.get('attachments')

    page.send(reciept_id, "Sucess, What should we call this prject?",)


@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    page.send(sender_id, 'When do you want {} done by?'. format(name),)

@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

    page.send(sender_id, 'Anything else I should know about your project?')


@page.handle_message
def message_handler(event):
    """:type event: fbmq.Event"""
    sender_id = event.sender_id
    message = event.message_text

page.send(recipient_id, Template.Receipt(recipient_name='Peter Chang',
                                            order_number='1234',
                                            currency='USD',
                                            payment_method='Visa 1234',
                                            timestamp="1428444852",
                                            elements=[element],
                                            address=address,
                                            summary=summary,
                                            adjustments=[adjustment]))