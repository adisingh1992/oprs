from wtforms import BooleanField
from flask_wtf import Form
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms import validators
from flask_wtf.file import FileField

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=8, max=100), validators.Required()], render_kw={"placeholder": "Username"})
    password = PasswordField('New Password', [validators.Length(min=8, message='Passwords Must Be 8 Letters Or More..!!'), validators.Required(), validators.EqualTo('confirm', message='Passwords Do Not Match..!!')], render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password', [validators.Required()], render_kw={"placeholder": "Confirm Password"})
    email = TextField('E-mail Id', [validators.Required(), validators.Email(message='Please Enter A Valid E-mail Address..!!')], render_kw={"placeholder": "Email"})
    fullname = TextField('Full Name', [validators.Required(), validators.Length(max=150)], render_kw={"placeholder": "Fullname"})
    contact = TextField('Contact Number', render_kw={"placeholder": "Contact Number"})
    reviewer = BooleanField('Wanna Be A Reviewer..!!')
    reviewer_choice = SelectField('Select A Subject', choices = [('SYSTEM', 'SYSTEM'), ('WEB', 'WEB'), ('APPLICATION', 'APPLICATION')])
    tos = BooleanField('I Accept Terms Of Service!', [validators.required()])
    submit = SubmitField("Register")
    
class LoginForm(Form):
    username = TextField('Username', [validators.Length(min=8, max=100), validators.Required()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', [validators.Length(min=8, message='Passwords Must Be 8 Letters Or More..!!'),validators.Required()], render_kw={"placeholder": "Password"})
    persistent = BooleanField("Remember Me..!!")
    submit = SubmitField("Login")
    
class PassReset(Form):
    username = TextField('Username', [validators.Length(min=8, max=100), validators.Required()], render_kw={"placeholder": "Username"})
    password = PasswordField('New Password', [validators.Length(min=8, message='Passwords Must Be 8 Letters Or More..!!'), validators.Required(), validators.EqualTo('confirm', message='Passwords Do Not Match..!!')], render_kw={"placeholder": "Password"})
    confirm = PasswordField('Confirm Password', [validators.Required()], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField("Submit")
    
class UploadFile(Form):
    author = TextField('Author', [validators.Length(min=8, max=200), validators.Required()], render_kw={"placeholder": "Author name"})
    email = TextField('E-mail Id', [validators.Required(), validators.Email(message='Please Enter A Valid E-mail Address..!!')], render_kw={"placeholder": "E-mail"})
    contact = TextField('Contact Number', [validators.Required()], render_kw={"placeholder": "Contact Number"})
    address = TextField('Address', [validators.Required()], render_kw={"placeholder": "Address"})
    title = TextField('Title', [validators.Length(max=255), validators.Required()], render_kw = {"placeholder": "Title For Article"})
    article_subject = SelectField('Select A Subject', choices = [('SYSTEM', 'SYSTEM'), ('WEB', 'WEB'), ('APPLICATION', 'APPLICATION')])
    article = FileField()
    submit = SubmitField("Submit")
    
class ReviewForm(Form):
    status = SelectField('Update Article Status', choices = [('ACCEPTED', 'ACCEPTED'), ('REJECTED', 'REJECTED'), ('MODIFY', 'MODIFY')])
    submit = SubmitField("Review")
    
class CommentForm(Form):
    comment = TextAreaField('Comment', [validators.Required()])
    submit = SubmitField("Comment")