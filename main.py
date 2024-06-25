from flask import Flask,request,render_template,session,redirect
from flask_cors import CORS
from models import create_post, getposts

import os,threading
import sqlite3
import datetime


#Social Network name = meen
app = Flask(__name__)

app.config["SECRET_KEY"] = ""


#table name= users


@app.route("/search", methods=["GET","POST"])
def searchuser():
    if session["logged_in_as"] == "user":
        return redirect('/')

    if request.method == "POST":
        username = request.form["searchuser"]
        if username != "":
            return redirect("/searchresults"+username)



    return render_template("searchuser.html",profile=session["logged_in_as"])




@app.route('/searchresults<user>', methods=["GET","POST"])
def search(user):
    if session["logged_in_as"] == "user":
        return redirect('/')

    if request.method == "POST":
        username = request.form["searchuser"]
        if (username != ""):
            return redirect("/searchresults"+username)

    con = sqlite3.connect("database.db")
    cursor = con.cursor()

    cursor.execute("""SELECT * FROM users""")

    con.commit()

    users = cursor.fetchall()

    return render_template("search.html",searchtag=user,users=users,profile=session["logged_in_as"])


@app.route('/unfollow<profile>')
def unfollow(profile):
    if session["logged_in_as"] == "user":
        return redirect('/')

    con = sqlite3.connect("database.db")
    cursor = con.cursor()

    cursor.execute(f"""SELECT * FROM {profile}_followed_by""")

    con.commit()

    followed_by = cursor.fetchall()

    if session["logged_in_as"] in followed_by[0]:
        cursor.execute(f"""DELETE FROM {profile}_followed_by WHERE followed_by_username='{session["logged_in_as"]}'""")
        con.commit()
        cursor.execute(f"""DELETE FROM {session['logged_in_as']}_following WHERE following_username='{profile}'""")
        con.commit()
    return redirect(f'/profile{profile}')

@app.route("/follow<profile>")
def follow(profile):
    if session["logged_in_as"] == "user":
        return redirect('/')

    con = sqlite3.connect("database.db")
    cursor = con.cursor()

    cursor.execute(f"""SELECT * FROM {profile}_followed_by""")

    con.commit()

    followed_by = cursor.fetchall()
    try:
        if (session["logged_in_as"],) not in followed_by:
            cursor.execute(f"""INSERT INTO {profile}_followed_by VALUES('{session["logged_in_as"]}')""")
            con.commit()
            cursor.execute(f"""INSERT INTO {session['logged_in_as']}_following VALUES('{profile}')""")
            con.commit()
        else:
            return "Already following"
    except Exception as e:
        print(e)
        cursor.execute(f"""INSERT INTO {profile}_followed_by VALUES('{session["logged_in_as"]}')""")
        con.commit()
        cursor.execute(f"""INSERT INTO {session['logged_in_as']}_following VALUES('{profile}')""")
        con.commit()

    return redirect(f'/profile{profile}')




@app.route('/profile<name>')
def profile(name):
    if session["logged_in_as"] == "user":
        return redirect('/')



    con = sqlite3.connect("database.db")


    cursor = con.cursor()

    try:
        cursor.execute(f"""SELECT * FROM {name}""")
        con.commit()
    except:
        return redirect("/")
    profile_data = cursor.fetchall()

    profile_data = profile_data[0]

    print(profile_data)

    bio = profile_data[0]

    profile_img = profile_data[1]

    display_name = profile_data[2]

    cursor.execute(f"""SELECT * FROM {name}_following""")
    con.commit()

    profile_following =  len(cursor.fetchall())

    cursor.execute(f"""SELECT * FROM {name}_followed_by""")
    con.commit()

    followed_by = len(cursor.fetchall())

    cursor.execute(f"""SELECT * FROM {name}_posts""")
    con.commit()

    posts = cursor.fetchall()

    cursor.execute(f"""SELECT * FROM {name}_followed_by""")

    con.commit()

    followed_by = cursor.fetchall()

    followed_by = followed_by

    following = False
    try:
        if (session["logged_in_as"],) not in followed_by:
            following = False
            print(session["logged_in_as"])
            print(followed_by)
        else:
            following = True
    except Exception as e:
        print(e)
        following = False
    return render_template("profile.html",isfollowing=following,logged_in=session["logged_in"],profile=session["logged_in_as"],profile_name=name,display_name=display_name,followers=len(followed_by),following=profile_following,bio=bio,profile_img=profile_img,posts=reversed(posts),username=name,logged_in_as=session["logged_in_as"])


@app.route('/logout')
def logout():
    if session["logged_in_as"] == "user":
        return redirect('/')

    session.clear()
    return redirect('/')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]


        credentials = (username,password)



        con = sqlite3.connect('database.db')

        cursor = con.cursor()

        cursor.execute('SELECT * FROM users')
        con.commit()

        if credentials in  cursor.fetchall():
            session["logged_in"] = "True"
            session["logged_in_as"] = username
            return redirect("/")

        else:
            return "Wrong credentials"






    return render_template("login.html",logged_in=session["logged_in"])




@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        bio = request.form["bio"]
        display_name = request.form["display_name"]
        credentials = (username,password)


        if " " in username:
            return "Wrong username"

        con = sqlite3.connect('database.db')

        cursor = con.cursor()

        cursor.execute('SELECT * FROM users')
        con.commit()
        if credentials not in cursor.fetchall():
            if request.files:
                img = request.files["profile_img"]

                img.save(f"static/{username}.png")
            print("Neni")
            cursor.execute(f"""INSERT INTO users VALUES ('{username}','{password}') """)
            con.commit()
            cursor.execute(f"""CREATE TABLE {username} (
            bio text,
            profile_img text,
            display_name text)""")

            cursor.execute(f"""INSERT INTO {username} VALUES ('{bio}','{username+".png"}','{display_name}') """)
            con.commit()
            cursor.execute(f"""CREATE TABLE {username}_following (
            following_username text)""")
            con.commit()

            cursor.execute(f"""CREATE TABLE {username}_followed_by (
            followed_by_username text)""")
            con.commit()
            cursor.execute(f"""CREATE TABLE {username}_posts (
            post text,
            datetime text)""")
            con.commit()

            return "account created"
        else:
            return "This user already exists"





    return render_template("register.html",logged_in=session["logged_in"])



@app.route('/upload', methods=['GET','POST'])
def upload():
    if session["logged_in_as"] == "user":
        return redirect('/')

    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save("static/"+uploaded_file.filename)
            create_post(session["logged_in_as"],uploaded_file.filename)
            con = sqlite3.connect("database.db")

            cursor = con.cursor()

            cursor.execute(f"""INSERT INTO {session['logged_in_as']}_posts VALUES('{uploaded_file.filename}','{datetime.datetime.now().date()}')""")

            con.commit()

    return render_template("upload.html",logged_in=session["logged_in"],profile=session["logged_in_as"])



@app.route('/', methods=['GET','POST'])
def forum():
    try:
        if session["logged_in"]:
            pass
    except:
        session["logged_in"] = "False"

    try:
        if session["logged_in_as"]:
            pass
    except:
        session["logged_in_as"] = "user"

    if session['logged_in_as'] == "user":
        return redirect("/login")


    print(session["logged_in"])
    name = ""
    posts = ""
    if request.method == 'POST':
        posts = request.form.get('post')

        name = session["logged_in_as"]
        try:
            create_post(name,posts)
            con = sqlite3.connect("database.db")
            cursor = con.cursor()

            cursor.execute(f"""INSERT INTO {name}_posts VALUES('{posts}','{datetime.datetime.now().date()}')""")

            con.commit()

            return redirect("/")
        except:
            pass
        name = ""
        posts = ""

    posts = getposts()
    return render_template("index.html", posts =reversed(posts),logged_in=session["logged_in"],profile=session["logged_in_as"])
app.run(debug=True)
#
