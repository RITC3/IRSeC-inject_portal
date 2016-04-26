#!flask/bin/python
from app import db, app
from flask import render_template, g, Blueprint, request, abort, send_from_directory, redirect, url_for
from flask.ext.security import current_user, login_required
from config import basedir
import os
import json
from app.models import *
from app.forms import *

# create a blueprint called main
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@main.route('/home')
def index():
    if g.user.is_authenticated and g.user.is_blueteam:
        return redirect(url_for('teamportal.team_portal'))
    blueteams = [x for x in User.query.all() if x.is_blueteam]
    return render_template("index.html", blueteams=blueteams)

@main.route('/files', defaults={'path': ''})
@main.route('/files/', defaults={'path': ''})
@main.route('/files/<path:path>')
@login_required
def files(path):
    base = os.path.join(basedir, "app", "static", "shared")
    f = os.path.join(base, path)
    if not os.path.abspath(f).startswith(base):
        flash("don't be a asshole", category="error")
        abort(404)
    if os.path.isfile(f):
        return send_from_directory(base, path)
    elif os.path.isdir(f):
        files = os.listdir(f)
        files = ([{"name": x+"/", "size": ""} for x in files if os.path.isdir(os.path.join(f, x))] +
                 [{"name": x, "size": size_fmt(os.path.getsize(os.path.join(f, x)))} for x in files if os.path.isfile(os.path.join(f, x))])
        dirname=os.path.relpath(f, base)
    else: abort(404)
    return render_template('files.html',
                           title="Shared files",
                           files=files,
                           dirname=dirname,
                           parent=os.pardir,
                           join=os.path.join)

@main.route('/api/announcements')
@login_required
def announcements():
    anns = list()
    for ann in Announcement.query.all():
        if ann.is_published and not ann.has_ended:
            anns.append(ann.text)
    return json.dumps(anns)

# http://stackoverflow.com/a/1094933
# expects bytes
def size_fmt(num):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
