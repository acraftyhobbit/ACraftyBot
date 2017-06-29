def fabric_callback_handler(event):
    from fbmq import QuickReply
    from lib.utilities import extract_data
    from server import page
    
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    image_id = payload.split('__')[-1]
    user_state[sender_id] = state[3]
    supply = dict()  # create a new supply object with the image_url, user_id etc.
    yes_no = [QuickReply(title="Yes", payload="YES"), QuickReply(title="No", payload="NO")]
    page.send(sender_id, "Do you know what you want to do with the fabric?", quick_replies=yes_no, metadata="supply.id")