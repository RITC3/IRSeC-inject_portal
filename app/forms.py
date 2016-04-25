from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, ValidationError, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import flash

"""
FlashForm: Adds a flash_errors function that will flash errors on the screen
Parent: flask.ext.wft.Form
"""
class FormFlash(Form):

    """flash_errors: iterate through form errors and flash them to the screen"""
    def flash_errors(self):
        for field, errors in self.errors.items():
            for error in errors:
                flash("{} - {}".format(field, error), category="error")


"""
InjectSubmitForm: parts to the inject submission form
Parent: .FlashForm
"""
class InjectSubmitForm(FormFlash):
    injectid = HiddenField("injectid")
    title = TextField('Submission Title', validators=[DataRequired()])
    note = TextAreaField('Note')
    allowed = FileAllowed(['pdf', 'doc', 'txt', 'rtf', 'docx', 'zip', 'tar', 'gz',
                           'png', 'jpg', 'jpeg', 'gif', 'xls', 'xlsx', 'ppt', 'pptx',
                           'xz', 'conf', 'csv'], 'That filetype is not allowed')
    attachment = FileField('Submission', validators=[allowed])
    submit = SubmitField("Submit")
