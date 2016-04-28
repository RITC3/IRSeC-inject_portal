#!flask/bin/python
from app import db, app
from flask import render_template, g, Blueprint, request, make_response, abort, redirect, url_for, send_from_directory
from flask.ext.security import current_user, login_required
from config import basedir
import os
from app.models import *
from app.forms import *
import json

# create a blueprint called injects
injects = Blueprint('injects', __name__, url_prefix="/injects")

@injects.route('/doc/<inject_id>')
@login_required
def doc(inject_id):
    inject = Inject.query.filter_by(id=inject_id).first_or_404()
    if not inject.is_published and not g.user.is_whiteteam:
        abort(404)
    base = os.path.join(basedir, "app", "injects")
    return send_from_directory(base, inject.inject_doc)

@injects.route('/submissions/files/<sub_id>')
@login_required
def submission_files(sub_id):
    sub = InjectSubmission.query.filter_by(id=sub_id).first_or_404()
    if not g.user.is_whiteteam and g.user != sub.user:
        abort(404)
    return send_from_directory(os.path.join(basedir, 'app', 'inject_submissions', sub.user.email), sub.attachment)

@injects.route('/api/list/<team_name>')
@login_required
def get_injects(team_name):
    team = User.query.filter_by(email=team_name).first_or_404()
    if not g.user.is_whiteteam and team.id != g.user.id:
        return "", 403
    inject_list = [ x for x in Inject.query.all() if x.is_published ]
    data = dict()
    data['data'] = list()
    for inject in inject_list:
        injectname = inject.name
        if inject.inject_doc:
            injectname += " <a href='" + url_for('injects.doc', inject_id=inject.id) + "'><i class='fa fa-paperclip'></i></a>"
        row = [inject.id, injectname, inject.publish_time_str,
               inject.end_time_str]
        submissions = InjectSubmission.query.filter_by(user_id=team.id, inject_id=inject.id).all()
        if len(submissions) > 0:
            row.append(str(len(submissions)) + " <button id='sub_view' class='btn btn-primary'>View</button>")
        else:
            row.append(len(submissions))
        disabled = ""
        extensions = [x for x in inject.extensions if g.user in x.teams and not x.has_ended]
        if not g.user.is_blueteam:
            disabled = " disabled='disabled'"
        if inject.has_ended and not len(extensions):
            row.append("<button class='btn btn-danger' disabled='disabled'>Closed</button>")
        elif inject.manual:
            row.append("<button id='inject_submit' class='btn btn-warning'" + disabled + ">Manual</button>")
        else:
            row.append("<button id='inject_submit' class='btn btn-success'" + disabled + ">Submit</button>")
        data['data'].append(row)
    return json.dumps(data)

@injects.route('/api/submissions/<team_name>/<inject_id>')
@login_required
def get_submissions(team_name, inject_id):
    team = User.query.filter_by(email=team_name).first_or_404()
    inject = Inject.query.filter_by(id=inject_id).first_or_404()
    if not g.user.is_whiteteam and team.id != g.user.id:
        return "", 403
    submission_list = InjectSubmission.query.filter_by(user=team, inject=inject).all()
    data = dict()
    data['data'] = list()
    for i, sub in enumerate(submission_list):
        row = [i+1, sub.title]
        if sub.attachment:
            row.append("<a href='" + url_for('injects.submission_files', sub_id=sub.id) +
                    "'>" + sub.attachment + "</a>")
        else:
            row.append("None")
        row.append(sub.timestamp_str)
        row.append(sub.notes)
        row.append("<button id='sub_delete-" + str(sub.id) + "' class='btn btn-danger'>Delete</button>")
        data['data'].append(row)
    return json.dumps(data)

@injects.route('/api/submissions/all')
@login_required
def all_injects():
    if not g.user.is_whiteteam:
        return "", 403
    data = dict()
    data['graded'] = list()
    data['ungraded'] = list()
    subs = InjectSubmission.query.all()
    for sub in subs:
        row = [sub.id, sub.inject.name, sub.user.email, sub.grade_str, sub.inject.value]
        row.append(("Yes" if sub.inject.manual else "No"))
        row.append(sub.timestamp_str)
        if sub.grade:
            row.append("<button id='grade' class='btn btn-primary'>Re-grade</button>")
            data['graded'].append(row)
        else:
            row.append("<button id='grade' class='btn btn-primary'>Grade</button>")
            data['ungraded'].append(row)
    return json.dumps(data)

@injects.route('/api/submissions/single/<sub_id>')
@login_required
def single_sub(sub_id):
    if not g.user.is_whiteteam:
        return "", 403
    sub = InjectSubmission.query.filter_by(id=sub_id).first_or_404()
    data = {"id": sub.id,
            "title": sub.title,
            "notes": sub.notes,
            "attachment": sub.attachment,
            "timestamp": sub.timestamp_str,
            "grade": sub.grade_str,
            "inject_id": sub.inject_id,
            "inject_name": sub.inject.name,
            "inject_val": sub.inject.value,
            "user_id": sub.user_id,
            "user_name": sub.user.email,
           }
    return json.dumps(data)

@injects.route('/api/grade/<sub_id>/<int:grade>')
@login_required
def grade_sub(sub_id, grade):
    if not g.user.is_whiteteam:
        return 403, ""
    sub = InjectSubmission.query.filter_by(id=sub_id).first_or_404()
    sub.grade = grade
    db.session.add(sub)
    db.session.commit()
    return "",200

@injects.route('/grade')
@login_required
def grade():
    if not g.user.is_whiteteam:
        abort(404)
    return render_template("grade.html", title="Inject Grading")

@injects.route('/api/submissions/delete/<sub_id>')
@login_required
def delete_submission(sub_id):
    sub = InjectSubmission.query.filter_by(id=sub_id).first_or_404()
    if not g.user.is_admin and g.user != sub.user:
        return "", 403
    if sub.attachment:
        os.remove(os.path.join(basedir, 'app', 'inject_submissions', sub.user.email, sub.attachment))
    db.session.delete(sub)
    db.session.commit()
    return "", 200
