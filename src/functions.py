from os import path
from MySQLdb import connect
from MySQLdb import escape_string as sanitize
from flask import session
from passlib.hash import sha512_crypt
from itsdangerous import URLSafeSerializer
from itsdangerous import TimedSerializer
from werkzeug.utils import secure_filename

def processRegistration(form):
    username = sanitize(form.username.data)
    password = sha512_crypt.encrypt(sanitize(form.password.data))
    email = sanitize(form.email.data)
    fullname = sanitize(form.fullname.data)
    contact = (sanitize(form.contact.data)) or None
    reviewer = form.reviewer.data
    reviewer_choice = sanitize(str(form.reviewer_choice.data))
        
    cursor, dbconn = dbConnection()
    status = None;
    
    query = "SELECT * FROM users WHERE username = %s"
    query_result = cursor.execute(query, [username])
    
    if int(query_result) > 0:
        status = "Plz..Choose A Different Username..!!"
    else:
        try:
            query = "INSERT INTO users(username, password, fullname, email_id, contact_no) VALUES(%s, %s, %s, %s, IFNULL(%s, DEFAULT(contact_no)));"
            query_result = cursor.execute(query, (username, password, fullname, email, contact))
            if reviewer == True:
                query = "INSERT INTO reviewers(user_id, subject) VALUES(LAST_INSERT_ID(), %s)"
                query_result = cursor.execute(query, [reviewer_choice])
            dbconn.commit()
            status = 0
        except:
            dbconn.rollback()
            status = "Oops.!! Something Went Wrong, Plz Try Again..!!"
    cursor.close()
    dbconn.close()
    return status

def processLogin(form):
    username = sanitize(form.username.data)
    password = sanitize(form.password.data)
    persistent = form.persistent.data
    
    status = False
    try:
        cursor, dbconn = dbConnection()
        query = "SELECT user_id, username, password FROM users WHERE username = %s"
        query_result = cursor.execute(query, [username])
        query_result = cursor.fetchone()
        user_id = query_result[0]
        query_result = query_result[2]
    except:
        status = "No Such User Exists..!!"
    else:
        if sha512_crypt.verify(password, query_result):
            session['logged_in'] = True
            session['username'] = username
            if persistent:
                session.permanent = True
            status = True
        else:
            status = "Invalid Credentials..!!"
        query = "SELECT reviewer_id, subject from reviewers where user_id = %s"
        query_result = cursor.execute(query, [user_id])
        if int(query_result) > 0:
            query_result = cursor.fetchone()
            session['reviewer'] = query_result[0]
            session['subject'] = query_result[1]
    cursor.close()
    dbconn.close()
    return status

def processReset(form):
    username = sanitize(form.username.data)
    password = sanitize(form.password.data)
    email = None
    status = None
    token = None

    cursor, dbconn = dbConnection()
    query = "SELECT * FROM users WHERE username = %s"
    query_result = cursor.execute(query, [username])
    if int(query_result) <= 0:
        status = "No Such User Exists..!!"
    else:
        email = cursor.fetchone()[4]
        url_serial = URLSafeSerializer("XHhkMVx4OTgzXFxceDhmZilceDk2Ilx4MTZceDhkXHhhYlx4ZGFceDlkXHhiYUNHXHhlM1x4YTRceDFiK0RceGNhfg==")
        timed_serial = TimedSerializer("XHhkMVx4OTgzXFxceDhmZilceDk2Ilx4MTZceDhkXHhhYlx4ZGFceDlkXHhiYUNHXHhlM1x4YTRceDFiK0RceGNhfg==")
        token = timed_serial.dumps(url_serial.dumps([username, password]))
    cursor.close()
    dbconn.close()
    return status, email, token

def resetVerifyCheck(key):
    url_serial = URLSafeSerializer("XHhkMVx4OTgzXFxceDhmZilceDk2Ilx4MTZceDhkXHhhYlx4ZGFceDlkXHhiYUNHXHhlM1x4YTRceDFiK0RceGNhfg==")
    timed_serial = TimedSerializer("XHhkMVx4OTgzXFxceDhmZilceDk2Ilx4MTZceDhkXHhhYlx4ZGFceDlkXHhiYUNHXHhlM1x4YTRceDFiK0RceGNhfg==")
    status = None
    try:
        key = timed_serial.loads(key, max_age = 300)
        key = url_serial.loads(key)

        username = str(sanitize(key[0]))
        password = sha512_crypt.encrypt(sanitize(key[1]))
    except:
        status = "Oops, The Link Has Expired..!!"
        return status
    cursor, dbconn = dbConnection()
    query = "UPDATE users SET password = %s WHERE username = %s"
    try:
        cursor.execute(query, (password, username))
        dbconn.commit()
        status = "Password Updated Successfully..!!"
    except:
        dbconn.rollback()
        status = "Oops, Something Went Wrong Please Try Again..!!"
    cursor.close()
    dbconn.close()
    return status

def uploadArticle(form, file_obj):
    author = sanitize(form.author.data)
    email = sanitize(form.email.data)
    contact = sanitize(form.contact.data) or None
    address = sanitize(form.address.data)
    title = sanitize(form.title.data)
    article_subject = sanitize(str(form.article_subject.data))
    
    cursor, dbconn = dbConnection()
    
    query = "SELECT `AUTO_INCREMENT` FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'articles'";
    article_id = cursor.execute(query)
    article_id = cursor.fetchone()[0]
    
    status = uploadFiles(file_obj, article_id)
    if status == True:
        try:
            query = "INSERT INTO articles(title, subject, review_date) VALUES(%s, %s, DEFAULT(review_date));"
            cursor.execute(query, (title, article_subject))
            
            query = "SELECT author_id FROM authors WHERE email_id = %s;"
            author_status = cursor.execute(query, [email])
            if int(author_status) > 0:
                author_id = cursor.fetchone()[0]
                query1 = "INSERT INTO article_author VALUES(%s, %s);"
                cursor.execute(query1, (article_id, author_id))
            else:
                query1 = "INSERT INTO authors(fullname, email_id, address, contact_no) VALUES(%s, %s, %s, IFNULL(%s, DEFAULT(contact_no)));"
                query2 = "INSERT INTO article_author VALUES(%s, LAST_INSERT_ID());"
                cursor.execute(query1,(author, email, address, contact))
                cursor.execute(query2, [article_id])
            dbconn.commit()
            status = "Article Uploaded Successfully"
        except:
            dbconn.rollback()
            status = "Oops, Something Went Wrong Please Try Again..!!"
    cursor.close()
    dbconn.close()
    return status

def uploadFiles(file_obj, filename):
    UPLOAD_FOLDER = 'articles'
    if 'article' not in file_obj:
        return "No File Attached..!"
           
    uploaded_file = file_obj['article']
    
    if uploaded_file.filename == '':
        return "No File Selected"

    try:
        if uploaded_file and allowedFiles(secure_filename(uploaded_file.filename)):
            uploaded_file.save(path.join(UPLOAD_FOLDER, str(filename)))
            return True
        return "Invalid File..!!"
    except:
        return "Oops, Something Went Wrong Please Try Again..!!"

def allowedFiles(filename):
    ALLOWED_EXTENSIONS = set(['txt'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def listArticles():
    cursor, dbconn = dbConnection()
    query = "SELECT article_id, title, submit_date FROM articles;"
    query_result = cursor.execute(query)
    query_result = cursor.fetchall()
    length = len(query_result)
    excerpts = []
    for id in range(1, length+1):
        excerpts.append(getArticleExcerpt(id))
    cursor.close()
    dbconn.close()
    return query_result, excerpts

def getArticleExcerpt(filename):
    UPLOAD_FOLDER = "articles"
    try:
        filepath = path.join(UPLOAD_FOLDER, str(filename))
        article = open(filepath, 'r')
        article = article.readline()
        return article
    except:
        return "Article Not Found..!!"

def viewArticle(filename):
    UPLOAD_FOLDER = "articles"
    article = None
    status = True
    filename = sanitize(filename)
    cursor, dbconn = dbConnection()
    query = "SELECT articles.article_id, articles.title, articles.subject, articles.status, articles.submit_date, articles.review_date, authors.fullname FROM articles INNER JOIN article_author ON articles.article_id = article_author.article_id INNER JOIN authors ON article_author.author_id = authors.author_id WHERE articles.article_id = %s"
    article_details = cursor.execute(query, [filename])
    article_details = cursor.fetchone()
    try:
        filepath = path.join(UPLOAD_FOLDER, str(filename))
        article = open(filepath, 'r')
        article = article.read()
    except:
        status = "Oops, Something Went Wrong Please Try Again..!!"
    comment = viewComment(filename, cursor)
    cursor.close()
    dbconn.close()
    return article_details, article, status, comment

def reviewArticle(form, article_id):
    article_status = sanitize(str(form.status.data))
    article_id = sanitize(str(article_id))
    reviewer_id = session['reviewer']
    status = None
    cursor, dbconn = dbConnection()
    try:
        query = "UPDATE articles SET status = %s, review_date = CURRENT_TIMESTAMP WHERE article_id = %s;"
        query1 = "INSERT INTO article_reviewer VALUES(%s, %s);"
        cursor.execute(query, (article_status, article_id))
        cursor.execute(query1, (article_id, reviewer_id))
        status = "Review Submitted Successfully..!!"
        dbconn.commit()
    except:
        dbconn.rollback()
        status = "Oops, Something Went Wrong Please Try Again..!!"
    cursor.close()
    dbconn.close()
    return status

def viewComment(filename, cursor):
    query = "SELECT users.fullname, comments.comment FROM comments INNER JOIN reviewers ON reviewers.reviewer_id = comments.reviewer_id INNER JOIN users ON reviewers.user_id = users.user_id WHERE article_id = %s;"
    query_result = cursor.execute(query, [filename])
    query_result = cursor.fetchall()
    return query_result

def commentArticle(form, article_id):
    status = "Thanks For Your Comment..!!"
    cursor, dbconn = dbConnection()
    article_id = sanitize(str(article_id))
    reviewer_id = session['reviewer']
    comment = sanitize(str(form.comment.data))
    try:
        if not (addComment(article_id, reviewer_id, comment, cursor, dbconn)):
            status = "You've Already Provided Your Comment..!!"
    except:
        dbconn.rollback()
        status = "Oops, Something Went Wrong Please Try Again..!!"
    return status

def addComment(article_id, reviewer_id, comment, cursor, dbconn):
    status = True
    query = "SELECT * FROM comments WHERE article_id = %s AND reviewer_id = %s;"
    query_result = cursor.execute(query, (article_id, reviewer_id))
    if int(query_result) > 0:
        status = False
    else:
        try:
            query = "INSERT INTO comments(article_id, reviewer_id, comment) VALUES(%s, %s, %s);"
            cursor.execute(query, (article_id, reviewer_id, comment))
            dbconn.commit()
        except:
            dbconn.rollback()
            status = False
    return status

def viewTopComments():
    cursor, dbconn = dbConnection()
    query = "SELECT users.fullname, comments.comment FROM comments INNER JOIN reviewers ON reviewers.reviewer_id = comments.reviewer_id INNER JOIN users ON reviewers.user_id = users.user_id LIMIT 7;"
    query_result = cursor.execute(query)
    query_result = cursor.fetchall()
    return query_result

def dbConnection():
    dbconn = connect(host='localhost', port=3306, user='root', passwd='password', db='oprs')
    cursor = dbconn.cursor()
    return cursor, dbconn