from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.security import UserMixin, RoleMixin
from datetime import datetime, timedelta

""" a third table must be created to relate users to roles by id.
    this is an example of a many-to-many relationship in SQLAlchemy
    i.e. a user can have many roles and roles can have many users
"""
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

extensions_users = db.Table('extensions_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('ext_id', db.Integer(), db.ForeignKey('injectextension.id')))

"""
User: defines users and their attribles for the website
Parents: db.Model, flask.ext.security.UserMixin
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(50))
    current_login_ip = db.Column(db.String(50))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    extensions = db.relationship('InjectExtension', lazy='dynamic', backref='teams',
                                 secondary=extensions_users)


    """flask admin needs this to print the user correctly"""
    def __str__(self):
        return self.email

    """
    hybrid_property is cool. this is a lame example, but you can do complex
    operations in the function and it can be called as an attribute
    to tell if a user is an admin I would do user.is_admin instead of
    user.is_admin() like a normal function
    """
    @hybrid_property
    def is_admin(self):
        return self.has_role('admin')

    @hybrid_property
    def is_blueteam(self):
        return self.has_role('blueteam')

    @hybrid_property
    def is_whiteteam(self):
        return self.has_role('whiteteam') or self.has_role('admin')


"""
Role: the table for roles on the site
Parents: db.Model, flask.ext.security.RoleMixin
"""
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    """flask admin needs this to print the role correctly"""
    def __str__(self):
        return self.name


class Inject(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    inject_doc = db.Column(db.String(1000))
    value = db.Column(db.Integer, nullable=False)
    publish = db.Column(db.Boolean, default=True)
    publish_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    end_time = db.Column(db.DateTime, nullable=False, default=datetime.now())
    manual = db.Column(db.Boolean, default=False)
    extensions = db.relationship('InjectExtension', lazy='dynamic', backref='inject')

    """flask admin needs this to print the object correctly"""
    def __str__(self):
        return self.name

    @hybrid_property
    def has_ended(self):
        if self.end_time and datetime.now() > self.end_time:
            return True
        return False

    @hybrid_property
    def is_published(self):
        if self.publish and datetime.now() > self.publish_time:
            return True
        return False

    @hybrid_property
    def publish_time_str(self):
        if self.publish_time:
            return self.publish_time.strftime('%A, %B %d, %Y, %I:%M %p')

    @hybrid_property
    def end_time_str(self):
        if self.end_time:
            return self.end_time.strftime('%A, %B %d, %Y, %I:%M %p')


class InjectSubmission(db.Model):
    __tablename__ = "injectsubmission"
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(60))
    notes = db.Column(db.String(500))
    attachment = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.now())
    inject_id = db.Column(db.Integer, db.ForeignKey('inject.id'), nullable=False)
    inject = db.relationship("Inject", foreign_keys=[inject_id])
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", foreign_keys=[user_id])
    grade = db.Column(db.Integer)

    """flask admin needs this to print the object correctly"""
    def __str__(self):
        return self.title

    @hybrid_property
    def grade_str(self):
        if self.grade:
            return str(self.grade)
        return "None"

    @hybrid_property
    def timestamp_str(self):
        return self.timestamp.strftime('%A, %B %d, %Y, %I:%M %p')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    published = db.Column(db.Boolean, default=True)
    publish_time = db.Column(db.DateTime, default=datetime.now())
    end_time = db.Column(db.DateTime)

    """flask admin needs this to print the object correctly"""
    def __str__(self):
        return self.name

    @hybrid_property
    def has_ended(self):
        if self.end_time and datetime.now() > self.end_time:
            return True
        return False

    @hybrid_property
    def is_published(self):
        if self.published and datetime.now() > self.publish_time:
            return True
        return False

class InjectExtension(db.Model):
    __tablename__ = "injectextension"
    id = db.Column(db.Integer, primary_key=True)
    inject_id = db.Column(db.Integer, db.ForeignKey('inject.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False) #in minutes
    start_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    @hybrid_property
    def has_ended(self):
        if datetime.now() > self.start_time + timedelta(minutes=self.duration):
            return True
        return False
