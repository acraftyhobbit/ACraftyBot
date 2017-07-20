"""CraftyBot."""
import os
import sys
from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session, abort
from fbmq import Page, Attachment, Template, QuickReply, NotificationType
from lib.model import User, Project, Proj_Stat, Status, Pattern, Image, Fabric, connect_to_db, db
from seed_status import create_status
from datetime import datetime, timedelta
from settings import crafter, server_host
app = Flask(__name__)
facebook = os.environ['FACEBOOK_TOKEN']
page = Page(facebook)
# Required to use Flask sessions and the debug toolbar
app.secret_key = ""

app.jinja_env.undefined = StrictUndefined

##############################################################################


@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Run once at the begining to connect to facebook api."""
    if request.method == 'POST':
        print request.get_data(as_text=True)
        page.handle_webhook(request.get_data(as_text=True))
        return "ok"
    else:
        challenge = request.args.get('hub.challenge')
        return challenge


@page.handle_message
def received_message(event):
    """Handle all incoming message from facebook."""
    from lib.message_handlers import handle_message
    handle_message(event=event)


@page.callback(['NEW_PROJECT'])
def task_new_project(payload, event):
    """User selected new project from main menu options."""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}
    crafter[sender_id]['current_route'] = 'new_project'
    page.send(sender_id, "Great. What would you like to call this project?")


@page.callback(['UPDATE_STATUS'])
def task_update_status(payload, event):
    """User selected update status from main menu options."""
    from lib.utilities import extract_data, work_inprogress
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}
    crafter[sender_id]['current_route'] = 'update_status'

    in_progress = work_inprogress(sender_id=sender_id)
    quick_replies = list()
    for name, project_id, due_at in in_progress:
        quick_replies.append(QuickReply(title=name, payload="project_{}".format(project_id)))

    page.send(sender_id, "Great. Which project do you want to update?", quick_replies=quick_replies)


@page.callback(['STOCK'])
def task_new_stock(payload, event):
    """User selected to add to stock from main menu options."""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}
    crafter[sender_id]['current_route'] = 'add_stock'
    stock_type = [QuickReply(title="Fabric Stock", payload="FABRIC_STOCK"), QuickReply(title="Pattern Stock", payload="PATTERN_STOCK")]
    page.send(sender_id, "Great. Which stock do you want to update?", quick_replies=stock_type)


@page.callback(['(.+)_STOCK'])
def callback_clicked_fabric_stock(payload, event):
    """User selects fabric button"""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}
    crafter[sender_id]['stock_type'] = payload.split('_')[0].lower()
    page.send(sender_id, "Upload your photo of the {} you want to add to stock.".format(crafter[sender_id]['stock_type']))


@page.callback(['project_(.+)'])
def select_project_callback(payload, event):
    """User selects a project from quick reply list to update."""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    if sender_id not in crafter.keys():
        crafter[sender_id] = {}
    project_id = int(payload.split('_')[-1])
    crafter[sender_id]['project_id'] = project_id
    page.send(sender_id, "Upload you newest project photo.")


@page.callback(['NOTE'])
def callback_clicked_note(payload, event):
    """User selects note button"""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    page.send(sender_id, "Please tell me the notes about this project")


@page.callback(['NO_NOTES'])
def callback_clicked_no_note(payload, event):
    """User selects no note button"""
    from lib.utilities import extract_data
    sender_id, message, message_text, message_attachments, quick_reply, = extract_data(event)
    page.send(sender_id, Template.Buttons("Your project has been saved. If you would like to get back to main menu type 'craftybot' again.", [{'type': 'web_url', 'title': 'Open Projects Home', 'value': server_host + '/user/{}/projects'.format(sender_id)}]))
    crafter[sender_id] = dict()


@app.route("/user/<user_id>/projects")
def all_projects(user_id):
    """Show list of projects."""
    project_dicts = list()
    user = User.query.filter(User.user_id == user_id).first()
    if user:
        projects = Project.query.filter(Project.fabric_id != None, Project.pattern_id != None, Project.due_at != None, Project.user_id == user_id).order_by(Project.project_id).all()
        for project in projects:
            project_dict = dict(
                project_id=project.project_id,
                name=project.name,
                fabric_image=project.fabric.image.url,
                pattern_image=project.pattern.image.url,
                status_images=[stat.image.url for stat in project.proj_stat])
            project_dicts.append(project_dict)
        return render_template("WIPprojects.html", projects=project_dicts, user_id=user_id)
    else:
        abort(404)

@app.route("/user/<user_id>/projects/<project_id>")
def project_details(user_id, project_id):
    """Show project details."""

    project = Project.query.filter(Project.project_id == project_id).first()
    if project and project.name and project.pattern and project.fabric and project.due_at:
        due_date = datetime.strftime(project.due_at, "%A, %B %d, %Y")
        return render_template("project-details.html", project=project, due_at=due_date)
    else:
        abort(404)

@app.route("/user/<user_id>/<stock_type>")
def stock_gallery(user_id, stock_type):
    """Show stock images."""
    if stock_type.lower() == 'pattern':
        stock = db.session.query(Pattern.pattern_id.label('id'), Image.url).join(Image).filter(Image.user_id == user_id).all()
    else:
        stock = db.session.query(Fabric.fabric_id.label('id'), Image.url).join(Image).filter(Image.user_id == user_id).all()
    if stock:
        return render_template("stock_gallery.html", stock=stock, stock_type=stock_type, user_id=user_id)
    else:
        abort(404)


@app.route("/add-to-project.json", methods=["POST"])
def add_to_projects():
    """Adds fabric or pattern stock to a new project."""
    from lib.utilities import add_stock_to_project, add_next_stock_response
    stock_id = request.form.get('id').encode('utf-8')
    user_id = request.form.get('user_id').encode('utf-8')
    stock_type = request.form.get('stock_type').encode('utf-8')
    project_id = crafter.get(user_id, dict()).get('project_id')
    if project_id:
        if stock_type == 'fabric':
            stock = Fabric.query.filter(Fabric.fabric_id == stock_id).first()
        else:
            stock = Pattern.query.filter(Pattern.pattern_id == stock_id).first()
        project = add_stock_to_project(stock=stock, project_id=project_id)
        crafter[user_id][stock_type + '_id'] = stock_id
        add_next_stock_response(sender_id=user_id, stock_type=stock_type)

    response = {'status': "success", 'id': stock_id}
    return jsonify(response)


@app.route("/user/<user_id>/due-at.json")
def add_due_date_calendar(user_id):
    """Displays project due dates on calendar."""
    from lib.utilities import work_inprogress
    inprogress = work_inprogress(sender_id=user_id)
    dates = []
    for project in inprogress:
        if project.due_at:
            due_at = datetime.strftime(project.due_at, "%Y %m %d")
            dates.append(dict(Date=due_at, Title=project.name, Link=server_host + "/user/{}/projects/{}".format(user_id, project.project_id)))
    return jsonify(dates)

@app.route("/user/<user_id>/incomplete-projects.json")
def display_incomplete_projects(user_id):
    """Generates the display information of projects that are only half complete."""
    user_id = request.form.get('user_id')
    incomp_projects = Project.query.filter(Project.due_at == None, Project.user_id == user_id).order_by(Project.project_id).all()
    for incomp_project in incomp_projects:
            incomp_project_dict = dict(
                project_id=incomp_project.project_id,
                name=incomp_project.name,
                fabric_image=incomp_project.fabric.image.url,
                pattern_image=incomp_project.pattern.image.url,
                status_images=[stat.image.url for stat in incomp_project.proj_stat])
            incomp_project_dicts.append(incomp_project_dict)

@app.route("/delete-project.json", methods=["POST"])
def delete_project_from_db():
    """Delete projects from data base selected by user."""
    from lib.utilities import delete_project
    project_id = request.form.get('id').encode('utf-8')
    user_id = request.form.get('user_id').encode('utf-8')
    print project_id
    delete_project(user_id=user_id, project_id=project_id)

    response = {'status': "success", 'id': project_id}
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
