#!flask/bin/python
from app import db, app
from flask import render_template, g, Blueprint, request, make_response, abort
from flask.ext.security import current_user, login_required
from werkzeug import secure_filename
from config import basedir
import os
from app.models import *
from app.forms import *

# create a blueprint called teamportal
teamportal = Blueprint('teamportal', __name__, url_prefix="/portals")

@login_required
@teamportal.route('/<team>', methods=['GET', 'POST'])
def team_page(team):
    team = User.query.filter_by(email=team).first_or_404()
    if not team.is_blueteam or (g.user.is_blueteam and g.user.id != team.id):
        abort(404)
    form = InjectSubmitForm()
    if request.method == 'POST':
        inject = Inject.query.filter_by(id=form.injectid.data).first_or_404()
        injectf = request.files['attachment']
        teamdir = os.path.join(basedir, 'app', 'inject_submissions', team.email)
        fn = secure_filename(injectf.filename)
        fpath = os.path.join(teamdir, fn)
        submit_form = True
        if injectf and os.path.exists(fpath):
            flash("The file you are trying to submit already exists, upload it with a different name")
            submit_form = False
        if inject.has_ended:
            flash("The submission period for this inject has expired")
            submit_form = False
        if form.validate_on_submit() and submit_form:
            #if g.user != team:
            #    abort(500)
            if injectf:
                if not os.path.exists(teamdir):
                    os.mkdir(teamdir)
                injectf.save(fpath)
            sub = InjectSubmission(title=form.title.data, notes=form.note.data,
                            attachment=fn, inject=inject, user=team)
            db.session.add(sub)
            db.session.commit()
            form.title.data = ""
            form.note.data = ""
            flash("Submission successful", category='good')
    else:
        form.flash_errors()
    return render_template("team.html", title="{} Portal".format(team), team=team, form=form)

@login_required
@teamportal.route('/')
def team_portal():
    return team_page(g.user.email)
