from flask import Flask,render_template,flash,redirect,url_for,session,logging,request,send_file,current_app,send_from_directory,g
from flask_mail import Mail,Message
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
import os
from bs4 import BeautifulSoup
import requests
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from tinytag import TinyTag
import sqlite3 as sql
from tinydb import TinyDB, Query
app=Flask(__name__)
name1=""
usernname1=""
email1=""
password1=""
username2=""
app.secret_key='secret123'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='farook100'
app.config['MYSQL_DB']='my_music'
app.config['MYSQL_CURSORCLASS']='DictCursor'
app.config['UPLOAD_FOLDER']='/music'
app.config['MAX_CONTENT_PATH']=5000000
app.config.from_pyfile('config.cfg')
mail=Mail(app)
s=URLSafeTimedSerializer('secret123')

mysql=MySQL(app)



@app.route('/')
def index():
    return render_template('index.html')



class RegisterForm(Form):
    name=StringField('Name',[validators.Length(min=1,max=50)])
    username=StringField('Username',[validators.Length(min=4,max=25)])
    email=StringField('Email',[validators.Length(min=6,max=50)])
    password=PasswordField('Password',[validators.DataRequired(),validators.EqualTo('confirm',message='Password do not match')])
    confirm=PasswordField('confirm Password')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/register',methods=['GET','POST'])
def register():
    form =RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(str(form.password.data))
        global usernname1,name1,email1,password1
        usernname1=username
        name1=name
        email1=email
        password1=password
        database = 'database.db'
        conn=sql.connect(database)
        conn1=sql.connect(database)
        token=s.dumps(email,salt='email-confirm')
        cur = conn.cursor()
        cur1= conn1.cursor()
        result=cur.execute("SELECT * FROM users WHERE username=?",(username,))
        result2=cur1.execute("SELECT * FROM users WHERE email=?",(email,))
        conn.commit()
        records=cur.fetchall()
        records1=cur1.fetchall()
        # for row in cur.fetchall():
        #     print(row)
        if len(records)>0:
            error='User name already exists,please try another user name'
            return render_template('register.html',form=form,error=error)
        if len(records1)>0:
            error='Email already exists,please try another Email'
            return render_template('register.html',form=form,error=error)
        else:
            cur.execute("INSERT INTO users(name,email,username,password) VALUES(?,?,?,?)",(name1,email1,usernname1,password1))
            conn.commit()
            conn.close()
            flash('Successfully created','success')
        return redirect(url_for('login'))
    
    return render_template('register.html',form=form)


#login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']

        password_candidate=request.form['password']
        database = 'database.db'
        conn = sql.connect(database)
        cur = conn.cursor()
        result=cur.execute("SELECT * FROM users WHERE username=?",(username,))
        record=cur.fetchall()
        conn.commit()
        if len(record)>0:
            data=record
            password=data[0][4]

            if sha256_crypt.verify(password_candidate,password):
                session['logged_in']=True
                session['username']=username
                session['id']=data[0][0]

                flash('login successful','success')
                return redirect(url_for('dashboard'))
            else:
                error='wrong password'
            return render_template('login.html',error=error)
            cur.close()
        else:
            error='Username not found'
            return render_template('login.html',error=error)

    return render_template('login.html')

#to prevent using of app without login
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('unauthorised,please login','danger')
            return redirect(url_for('login'))
    return wrap

#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('you are now logout','success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
    database = 'database.db'
    conn = sql.connect(database)
    cur = conn.cursor()
    share_url=app.config['APP_BASE_URL']+':'+app.config['APP_PORT']+'/play_playlist/'
    result=cur.execute("SELECT * from songs WHERE user_id = ?",(session['id'],))
    songs=cur.fetchall()

    if len(songs)>0:
        return render_template('dashboard.html',songs=songs,share_url=share_url)
    else:
        msg="NO PLAYLIST FOUND "

    return render_template('dashboard.html',msg=msg,share_url=share_url)
    cur.close()

@app.route('/upload_song')
@is_logged_in
def upload():
    

    return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
@is_logged_in
def upload_file():
   if request.method == 'POST':
           f = request.files['file']
           file_name = f.filename
           path=os.getcwd()+'\\static\\music\\'
           path1=path.replace('\\','/')
           path=path1+file_name
           f.save(os.path.join(path1,file_name))
           username=session['username']
           database = 'database.db'
           conn=sql.connect(database)
           cur=conn.cursor()
           row1=cur.execute("SELECT * FROM users WHERE username = ?",[username])
           result1=cur.fetchone()
           tag = TinyTag.get(path)
           album=tag.album
           title=tag.title
           artist=tag.artist
           id=result1[0]
           if title==None:
               title=path
               title=title.rsplit('/', 1)[-1]
           i_sql="insert into songs(title,path,album,artist,user_id) values (?,?,?,?,?)"
           val = (title,path,album,artist,id)
           cur.execute(i_sql, val)
           conn.commit()
           conn.close()
           return redirect(url_for('dashboard'))
   else:
       return redirect(url_for('dashboard'))

@app.route('/play_playlist/<string:idd>')
@is_logged_in
def play_playlist(idd):
    res=""
    playl=[]
    data=[]
    database = 'database.db'
    conn = sql.connect(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs WHERE id =?",(idd,))
    result=cur.fetchone()
    res=result[2]
    res=res.rsplit('/', 1)[-1]
    if res is None:
        flash("no song in playlist",'danger')
        return redirect(url_for('dashboard'))
    else:
        return render_template('playlist.html',albu=res)

@app.route('/download/<string:idd>')
def downloadFile (idd):
    res=""
    playl=[]
    data=[]
    database = 'database.db'
    conn = sql.connect(database)
    cur = conn.cursor()
    cur.execute("SELECT * FROM songs WHERE id =?",(idd,))
    result=cur.fetchone()
    res=result[2]
    res=res.rsplit('/', 1)[-1]
    if res is None:
        flash("no song in playlist",'danger')
        return redirect(url_for('dashboard'))
    else:
        return render_template('download.html',path=res)

@app.route('/delete_playlist/<string:idd>')
@is_logged_in
def delete_playlist(idd):
    database = 'database.db'
    conn = sql.connect(database)
    cur = conn.cursor()
    cur.execute("delete  FROM songs WHERE id =?",(idd,))
    conn.commit()
    cur.close()
    flash("Playlist successfully deleted",'success')
    return redirect(url_for('dashboard'))

@app.route('/search',methods=['POST'])
@is_logged_in
def new():
    string=""
    co=request.form['give']
    song=co
    # song_name=co+'.mp3'
    database = 'database.db'
    conn = sql.connect(database)
    cur = conn.cursor()
    result=cur.execute("SELECT * FROM songs WHERE title like ? or artist like ? or album like ? ",('%'+song+'%','%'+song+'%','%'+song+'%',))
    songs=cur.fetchall()
    
    if len(songs)>0:
        return render_template('search.html',songs=songs)
    else:
        msg="NO PLAYLIST FOUND "

    return render_template('search.html',msg=msg)
    cur.close()




@app.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    app.secret_key='secret123'
    app.run()