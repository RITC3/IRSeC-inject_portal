from flask.ext.admin import AdminIndexView, BaseView
from flask.ext.admin.contrib.sqla.view import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask.ext.security import utils
from wtforms import PasswordField, validators
from flask import redirect, url_for, flash, g
from os import listdir, path
from config import basedir

"""
AdminBaseView: Access control for the admin panel, without this there is none!
Parent: flask.ext.admin.BaseView
"""
class AdminBaseView(BaseView):
    """Who can see the admin page?"""
    def is_accessible(self):
        if g.user.is_authenticated and g.user.is_admin:
            return True
        return False

    """This is run when a user tries to visit an admin page"""
    def _handle_view(self, name, **kwargs):
            # add a check to make sure that the user has permission
            if not self.is_accessible():
                # if not then print an error and redirect
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))


"""
WhiteTeamBaseView: Access control for the admin panel, without this there is none!
Parent: flask.ext.admin.BaseView
"""
class WhiteTeamBaseView(BaseView):
    """Who can see the admin page?"""
    def is_accessible(self):
        if g.user.is_authenticated and g.user.is_whiteteam:
            return True
        return False

    """This is run when a user tries to visit an admin page"""
    def _handle_view(self, name, **kwargs):
            # add a check to make sure that the user has permission
            if not self.is_accessible():
                # if not then print an error and redirect
                flash("You don't have permission to go there", category="warning")
                return redirect(url_for('main.index'))


"""
WhiteTeamIndexView: Make AdminIndexView from flask.ext.admin require RBAC
Parents: flask.ext.admin.AdminIndexView, .WhiteTeamBaseView
"""
class ProtectedIndexView(AdminIndexView, WhiteTeamBaseView):
    pass


"""
AdminModelView: Add RBAC to flask-admin's model view
Parents: flask.ext.admin.contrib.sqla.view.ModelView, .AdminBaseView
"""
class AdminModelView(ModelView, AdminBaseView):
    pass


"""
WhiteTeamModelView: Add RBAC to flask-admin's model view
Parents: flask.ext.admin.contrib.sqla.view.ModelView, .AdminBaseView
"""
class WhiteTeamModelView(ModelView, WhiteTeamBaseView):

    def is_accessible(self):
        self.can_create = g.user.is_admin
        self.can_edit = g.user.is_admin
        self.can_delete = g.user.is_admin
        return super(WhiteTeamModelView, self).is_accessible()


"""
UserModelView: The model view for users
Parent: .AdminModelView
"""
class UserModelView(AdminModelView):
    # we don't need to see the huge password hash in the list display
    column_exclude_list = ['password']

    # this information should not be changed, so don't make it editable
    form_excluded_columns = ['last_login_at', 'current_login_at',
                             'last_login_ip', 'current_login_ip',
                             'login_count', 'submissions']

    # make sure the password can't be seen when typing it
    form_overrides = dict(password=PasswordField)

    # add a confirm password field and make sure it equals the other password field
    form_extra_fields = {'password2': PasswordField('Confirm Password',
                                                    [validators.EqualTo('password', message='Passwords must match')])}

    # this just sets the order of the form fields, otherwise confirm pass is on the bottom
    form_columns = ('roles', 'email', 'password', 'password2', 'active')

    # make sure the password is actually encrypted when it is changed or created!
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = utils.encrypt_password(model.password)


"""
RoleModelView: The model view for roles
Parent: .AdminModelView
"""
class RoleModelView(AdminModelView):
    # adding, deleting or changing role names would be useless...
    can_delete = False
    can_create = False
    form_excluded_columns = ('name')
    pass


"""
InjectModelView: The model view for Injects
Parent: .AdminModelView
"""
class InjectModelView(WhiteTeamModelView):
    files = filter(lambda f: not f.startswith("."), listdir(path.join(basedir, 'app', 'injects')))
    files = [(x, x) for x in files]
    form_choices = { 'inject_doc': files }
    form_args = { 'inject_doc': { 'validators': list() } }


"""
WhiteTeamFileAdmin: The file admin view for shared files
Parents: FileAdmin, WhiteTeamBaseView
"""
class WhiteTeamFileAdmin(FileAdmin, WhiteTeamBaseView):

    def is_accessible(self):
        self.can_delete = g.user.is_admin
        self.can_delete_dirs = g.user.is_admin
        return super(WhiteTeamFileAdmin, self).is_accessible()
