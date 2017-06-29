def handle message(event):
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if message_text and "craftybot" in message_text.lower():
        handle_case_1(event=event)

    elif message_text and user_state.get(sender_id) == state[0]:
        user_state[sender_id] = state[1]

        page.send(sender_id, "Please upload your first photo to start a new project", metadata="IMAGE_ONE")

    elif message_text and user_state.get(sender_id) == state[5]:
        user_state[sender_id] = state[6]
        note_no = [QuickReply(title="Note", payload="NOTE"), QuickReply(title="No Notes", payload="NO_NOTE")]
        page.send(sender_id, "Got it. Anything else you want me to know about this project", quick_replies=note_no, metadata="Due_Date")

    elif message_attachments and user_state.get(sender_id) == state[1]:
        image_id = 1  # add to db
        user_state[sender_id] = state[2]
        image_type = [QuickReply(title="Fabric", payload="FABRIC"), QuickReply(title="Pattern", payload="PATTERN")]
        page.send(sender_id, "What is this an image of?", quick_replies=image_type, metadata="message_attachments")

    elif message_attachments and user_state.get(sender_id) == state[4]:
        user_state[sender_id] = state[5]
        page.send(sender_id, "Success, How many weeks do you want to do this project?",)



def handle_case_1(event):
    from server import page
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)

    new_user = User.query.filter(User.user_id == sender_id).all()
    if not new_user:
        user = User(user_id=sender_id)
        db.session.add(user)
        db.session.commit()

    craftybot = [QuickReply(title="New Project", payload="NEW_PROJECT"), QuickReply(title="Update Status", payload="UPDATE_STATUS")]
    page.send(sender_id, "How may I help you today?", quick_replies=craftybot, metadata='now it is a string')