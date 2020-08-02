Flask-Music-app
A Simple MUsic web app with flask as framework in python, mysql as database that can play music,manage playlists,Download songs,etc.

Prerequisites
Python 3.0
mysql

Packages required:
flask
passlib
flask_mail
flask_mysqldb
wtforms
bs4
TinyTag

Installing Packages
* Do pip3 install -r requirements.txt
Import sql table
* Create Database named as my_music.
* run all .sql files placed under music.sql with root user
* Make sure you truncate all the tables 

How to Run app:
* Clone the repo to your local machine.
* Install the above given packages.
* Replace the app.config['MYSQL_PASSWORD']='Enter your sqlpassword'( line 24 in app.py) with you sql password.
* Replace the Email and password in config.cfg with Email and password of mail from which you want to send the confirmation. mail.
* Replace the upload folder in config.cfg with the full folder name. Make sure the folder is inside the static folder. ex: '/home/ubuntu/music_app/static/music'
* Then do python3 app.py.
* open http://127.0.0.1:5000/ in Your local browser.

Features
 * Login
 * Register and verify using Confirmation mail.
 * Play albums using music player.
 * Download any song of your choice.

How to Contribute:
  * Fork the project using the fork option.
  * Clone this repository to your local machine.
  * Now add upstream by using command - **git remote add upstream "name of my repo"**
  * Create a new branch on your local machine.
  * Start contributing and make a pull request to apply these changes.

You can report any other issues also