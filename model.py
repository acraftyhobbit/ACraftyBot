
from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "user"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    name = db.Colume(db.Text, nullable=False)
    #facebook = db.Column(db.Text, nullable = False)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<User user_id={} email={}>" .format(self.user_id, self.email)


class Project(db.Model):
    """User of ratings website."""

    __tablename__ = "project"

    project_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    proj_plan_id = db.Column(db.Integer, db.ForeignKey('proj_plan.proj_plan_id'))
    proj_stat_id = db.Column(db.Integer, db.ForeignKey('proj_stat.proj_stat_id'))
    name = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    due_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Project project_id={} name={}>" .format(self.project_id, self.name)


class Proj_Stat(db.Model):
    """User of ratings website."""

    __tablename__ = "proj_stat"

    proj_stat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projecr.project_id'))
    url = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Proj_Stat proj_stat_id={} stats_id ={} url={}>" .format(self.project_stat_id, self. status_id, self.url)


class Status(db.Model):
    """User of ratings website."""

    __tablename__ = "status"

    status_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    status = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Status status_id={} status={}>" .format(self.status_id, self.status)


class Proj_Plan(db.Model):
    """User of ratings website."""

    __tablename__ = "proj_plan"

    proj_plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.plan_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projecr.project_id'))

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Proj_Plan project_id={} plan_id ={}>" .format(self.project_id, self. plan_id)


class Plan(db.Model):
    """User of ratings website."""

    __tablename__ = "plan"

    plan_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Plan plan_id={} name={} url={}>" .format(self.plan_id, self.name, self.url)

