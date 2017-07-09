##########################################
##Imports
##########################################
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_mail import Mail
from flask_mail import Message
from forms import UploadFile
from forms import PassReset
from forms import LoginForm
from forms import ReviewForm
from forms import CommentForm
from forms import RegistrationForm
from functions import commentArticle
from functions import viewTopComments
from functions import reviewArticle
from functions import viewArticle
from functions import listArticles
from functions import uploadArticle
from functions import processReset
from functions import processLogin
from functions import resetVerifyCheck
from functions import processRegistration
##########################################

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

##########################################
##Mail Configuration
##########################################
mail = Mail()
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'adi.singh1992@gmail.com'
app.config["MAIL_PASSWORD"] = '2don2dtitq'
mail.init_app(app)
##########################################

##########################################
##Views
##########################################
@app.route('/')
def index():
    comments = viewTopComments()
    return render_template('index.html', comments=comments)

@app.route('/home/')
def home():
    if 'logged_in' not in session:
        flash("You Have To Login First To Access This Page..!!")
        return redirect(url_for('login'))
    articles, excerpts = listArticles()
    length = len(articles)
    return render_template('home.html', articles=articles, excerpts=excerpts, length=length)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        flash("You're Already Logged-In..!!")
        return redirect(url_for('home'))
    form = RegistrationForm(request.form)
    reg_result = ''
    if request.method == 'POST' and form.validate():
        reg_result = processRegistration(form)
        if reg_result == 0:
            flash('Thanks For Registering..!!')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, error=reg_result)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        flash("You're Already Logged-In..!!")
        return redirect(url_for('home'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        login_result = processLogin(form)
        if login_result == True:
            return redirect(url_for('home'))
        else:
            flash(login_result)
    return render_template('login.html', form=form)

@app.route('/logout/')
def logout():
    if 'logged_in' in session:
        session.clear()
        flash("You've Been Successfully Logged-Out..!!")
    else:
        flash("You're Not Logged In..!!")
    return redirect(url_for('index'))

@app.route('/reset/', methods=['GET', 'POST'])
def passReset():
    if 'logged_in' in session:
        flash("You're Already Logged-In..!!")
        return redirect(url_for('home'))
    form = PassReset(request.form)
    if request.method == 'POST' and form.validate():
        reset_result, email, token = processReset(form)
        if email is not None and reset_result is None:
            try:
                msg = Message("Password Reset (OPRS)", sender='adi.singh1992@gmail.com', recipients=[email])
                token = "Go To The Following URL To Succesfully Change Your Password..!!:- localhost:5000/reset/%s" %token
                msg.body = token
                mail.send(msg)
                flash("Follow The Link Sent To Your E-mail Account To Complete The Process Successfully..!!")
            except:
                flash("Oops, Something Went Wrong, Please Try Again..!!")
        else:
            flash(reset_result)
    return render_template('reset.html', form=form)

@app.route('/reset/<key>')
def resetVerify(key):
    verify_result = resetVerifyCheck(key)
    flash(verify_result)
    return redirect(url_for('login'))

@app.route('/uploads/', methods=['GET', 'POST'])
def uploads():
    if 'logged_in' not in session:
        flash("You Have To Login First To Access This Page..!!")
        return redirect(url_for('login'))
    form = UploadFile(request.form)
    if request.method == 'POST' and form.validate():
        file_obj = request.files
        upload_status = uploadArticle(form, file_obj)
        flash(upload_status)
    return render_template('uploads.html', form=form)

@app.route('/view/<filename>', methods=['GET', 'POST'])
def displayArticle(filename):
    if 'logged_in' not in session:
        flash("You Have To Login First To Access This Page..!!")
        return redirect(url_for('login'))
    details, article, status, comment = viewArticle(filename)
    if status == True:
        return render_template('view.html', form=ReviewForm(), form1=CommentForm(), details=details, article=article, comment=comment)
    flash(status)
    return redirect(url_for('home'))

@app.route('/review/<filename>', methods=['POST'])
def review(filename):
    if 'logged_in' and 'reviewer' not in session:
        flash("You Are Not Authorized To Access This Page..!!")
        return redirect(url_for('login'))
    form = ReviewForm(request.form)
    if form.validate():
        review_result = reviewArticle(form, filename)
        flash(review_result)
    return redirect(request.referrer)

@app.route('/comment/<filename>', methods=['POST'])
def comment(filename):
    if 'logged_in' and 'reviewer' not in session:
        flash("You Are Not Authorized To Access This Page..!!")
        return redirect(url_for('login'))
    form = CommentForm(request.form)
    if form.validate():
        comment_result = commentArticle(form, filename)
        flash(comment_result)
    return redirect(request.referrer)

@app.route('/comments/')
def comments():
    comments = viewTopComments()
    return render_template('comments.html', comments=comments)
##########################################

##########################################
##Application Initialization
##########################################
if __name__ == "__main__":
    app.secret_key = 'XHhkMVx4OTgzXFxceDhmZilceDk2Ilx4MTZceDhkXHhhYlx4ZGFceDlkXHhiYUNHXHhlM1x4YTRceDFiK0RceGNhfg=='
    app.run(debug=True)
##########################################