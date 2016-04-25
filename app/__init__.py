#!flask/bin/python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, utils
from config import FIRST_USER_PASS, FIRST_USER_NAME, basedir
from flask_wtf.csrf import CsrfProtect
from flask_admin.contrib.sqla import ModelView
from flask.ext.admin import Admin
from flask_admin.base import MenuLink
import os

# initialize the application, import config, setup database, setup CSRF protection
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
CsrfProtect(app)

# set up the database model if not already set up
from app import models
db.create_all()
db.session.commit()

# setup the User/Role tables with flask-security, create base users/groups if neccessary
userstore = SQLAlchemyUserDatastore(db, models.User, models.Role)
sec = Security(app, userstore)
try:
    with app.app_context():
        userstore.find_or_create_role(name='admin', description='Administrator')
        userstore.find_or_create_role(name='blueteam', description='Blue team accounts')
        userstore.find_or_create_role(name='whiteteam', description='White team accounts')
        userstore.create_user(email=FIRST_USER_NAME,
                            password=utils.encrypt_password(FIRST_USER_PASS))
        userstore.create_user(email="team0",
                            password=utils.encrypt_password("team0"))
        userstore.add_role_to_user(FIRST_USER_NAME, 'admin')
        userstore.add_role_to_user("team0", 'blueteam')
        db.session.commit()
except: db.session.rollback()

# get the view controllers for the app
from app.views import main, teamportal, admin, common, injects

# set up main as a blueprint, add as many blueprints as necessary
app.register_blueprint(main.main)
app.register_blueprint(teamportal.teamportal)
app.register_blueprint(injects.injects)

# configure the admin interface, populate it with pages and links
app_admin = Admin(app, 'IRSeC Inject Portal Admin', template_mode='bootstrap3', index_view=admin.ProtectedIndexView())
app_admin.add_view(admin.InjectModelView(models.Inject, db.session))
app_admin.add_view(admin.SharedFileAdmin(os.path.join(basedir, "app", "static", "shared"), '/shared/', name="Shared Files"))
app_admin.add_view(admin.InjectFileAdmin(os.path.join(basedir, "app", "injects"), '/injects/', name="Inject Files"))
app_admin.add_view(admin.UserModelView(models.User, db.session))
#app_admin.add_view(admin.RoleModelView(models.Role, db.session))
app_admin.add_link(MenuLink(name='Back to Site', url='/'))
