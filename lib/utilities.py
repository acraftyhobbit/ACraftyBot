def extract_data(event):
    sender_id = event.sender_id
    message = event.message
    message_text = message.get("text")
    message_attachments = message.get("attachments")
    quick_reply = message.get("quick_reply")
    #payload = quick_reply.get('payload')

    return sender_id, message, message_text, message_attachments, quick_reply
