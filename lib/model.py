
from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ACraftyBot."""

    __tablename__ = "user"

    user_id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<User user_id={}>" .format(self.user_id,)


class Project(db.Model):
    """Projects created between user and ACraftyBot."""

    __tablename__ = "project"

    project_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id'))
    pattern_id = db.Column(db.Integer, db.ForeignKey('pattern.pattern_id'))
    fabric_id = db.Column(db.Integer, db.ForeignKey('fabric.fabric_id'))
    name = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    due_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="project")
    fabric = db.relationship("Fabric", backref="project")
    pattern = db.relationship("Pattern", backref="project")

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Project project_id={} name={}>" .format(self.project_id, self.name)


class Proj_Stat(db.Model):
    """Status of particular projects."""

    __tablename__ = "proj_stat"

    proj_stat_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    created_at = db.Column(db.DateTime)

    image = db.relationship("Image", backref="proj_stat")
    project = db.relationship("Project", backref="proj_stat")
    status = db.relationship("Status", backref="proj_stat")

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Proj_Stat proj_stat_id={} stats_id ={}>" .format(self.project_stat_id, self. status_id,)


class Status(db.Model):
    """THe different status types."""

    __tablename__ = "status"

    status_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Status status_id={} status={}>" .format(self.status_id, self.name)


class Pattern(db.Model):
    """The patterns being used for a project."""

    __tablename__ = "pattern"

    pattern_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    name = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)

    image = db.relationship("Image", backref="pattern")

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Plan pattern_id={} name={}>" .format(self.pattern_id, self.name,)


class Fabric(db.Model):
    """The fabric being used for a project."""

    __tablename__ = "fabric"

    fabric_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.image_id'))
    name = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)

    image = db.relationship("Image", backref="fabric")

class Image(db.Model):
    """The images being used for a project."""

    __tablename__ = "image"

    image_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.user_id'))
    url = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        """Provide helpful representation when printing."""

        return "<Image image_id={} name={}>" .format(self.image_id, self.name,)


##############################################################################
# Helper functions


def connect_to_db(app, db_uri="postgresql:///craftydata"):
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def example_data():
    """Create example data for the test database."""
    user = User(user_id=1397850150328689, created_at='now')

    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':

    import sys
    sys.path.append('..')

    from server import app
    connect_to_db(app)