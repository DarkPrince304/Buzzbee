from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack

from dbconnect import connection
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from app import app

from flask_bootstrap import Bootstrap

class RegistrationForm(Form):
	username = TextField("Username", [validators.Length(min=4, max=20)])
	email = TextField("Email Address", [validators.Length(min=6, max=50)])
	password = PasswordField("Password", [validators.Required(),
										  validators.EqualTo("confirm", message = "Passwords must match!"),
										  validators.Length(min=6, max=30)])
	confirm = PasswordField("Repeat Password")


class LoginForm(Form):
	username = TextField("Username")
	password = PasswordField("Password")

@app.route('/', methods = ['POST', 'GET'])
@app.route('/index/', methods = ['POST', 'GET'])
@app.route('/home/', methods = ['POST', 'GET'])
def index():
	try:
		formReg = RegistrationForm(request.form)
		formLog = LoginForm(request.form)
		return render_template("home.html", formReg = formReg, formLog = formLog)
	except Exception as e:
		return str(e)

@app.route('/register/', methods = ["POST", "GET"])
def register():
	try:
		errorLog = ''
		errorReg = ''
		formReg = RegistrationForm(request.form)
		formLog = LoginForm(request.form)
		if request.method == "POST" and formReg.validate():
			username = formReg.username.data
			email = formReg.email.data
			password = sha256_crypt.encrypt((str(formReg.password.data)))
			c, conn = connection()
			x = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))
			if int(x) > 0:
				errorReg = "That username is taken."
				print("That username is already taken please choose another")
				return render_template("home.html", formReg = formReg, formLog = formLog, errorLog = errorLog, errorReg = errorReg)
			else:
				c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
				(thwart(username),thwart(password),thwart(email)))
				uid = c.execute("SELECT uid FROM users WHERE username = (%s)",(thwart(username)))
				conn.commit()
				c.close()
				conn.close()
				gc.collect()
				session["uid"]=uid
				session["logged_in"] = True
				session["username"] = username
				return redirect(url_for("news"))
	except Exception as e:
		return str(e)
	
@app.route('/login/', methods = ["POST", "GET"])
def login():
	try:
		errorLog = ''
		errorReg = ''
		formLog = LoginForm(request.form)
		formReg = RegistrationForm(request.form)
		if request.method == "POST":
			#print "Hello"
			username = formLog.username.data
			password = formLog.password.data
			#print username, password
			c, conn = connection()
			data = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))
			data = c.fetchone()[2]
			uid = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))
			uid = c.fetchone()[0]
			#print "hello",data, uid
			#print "Hello"
			if sha256_crypt.verify(password, data):
				session['uid'] = uid
				session['logged_in'] = True
				session['username'] = username
				gc.collect()
				return redirect(url_for("news"))
				#return render_template("test.html", username = session["username"], loggedIn = session["logged_in"])
			else:
				errorLog = "Invalid Credentials"
				return render_template('home.html', formLog = formLog, formReg = formReg, errorLog = errorLog, errorReg = errorReg)
	except Exception as e:
		errorLog = "Invalid credentials"
		return render_template ("home.html", formLog = formLog, formReg = formReg, errorLog = errorLog, errorReg = errorReg)

@app.route('/base/')
def base():
	return render_template("base.html")

@app.route('/news/')
def news():
	try:
		c, conn = connection()
		data1 = c.execute("SELECT username FROM photos")
		data1 = c.fetchall()
		data2 = c.execute("SELECT description FROM photos")
		data2 = c.fetchall()
		data3 = c.execute("SELECT link FROM photos")
		data3 = c.fetchall()
		users = []
		descs = []
		links = []
		for i in data1:
			users.append(str(i).strip("(),'"))
		for i in data2:
			descs.append(str(i).strip("(),'"))
		for i in data3:
			links.append(str(i).strip("(),'"))
		users.reverse()
		descs.reverse()
		links.reverse()
		print users
		print descs
		return render_template("news.html", usersdescslinks = zip(users,descs,links), username = session["username"], loggedIn = session["logged_in"])
	except Exception as e:
		return str(e)

@app.route('/logout/')
def logout():
	session['username']=''
	session['logged_in']=False
	return redirect(url_for("index"))

@app.route('/profile/')
def profile():
	print session["uid"]
	c, conn = connection()
	data1 = c.execute("SELECT link FROM photos WHERE uid = (%s)",thwart(str(session["uid"])))
	data1 = c.fetchall()
	data2 = c.execute("SELECT description FROM photos WHERE uid = (%s)",thwart(str(session["uid"])))
	data2 = c.fetchall()
	pics = []
	desc = []
	print data1,data2
	for i in data1:
		pics.append(str(i).strip("(),'"))
	for i in data2:
		desc.append(str(i).strip("(),'"))
	pics.reverse()
	desc.reverse()
	print desc
	return render_template("profile.html", username = session["username"], pics = zip(pics,desc))

@app.route('/uploadpic/')
def uploadpic():
	return render_template("uploadpic.html", username = session["username"], loggedIn = session["logged_in"])

@app.route('/save/', methods=["GET", "POST"])
def save():
	uid = session["uid"]
	#print "hello",uid
	link = request.json["link"]
	description = request.json["description"]
	likes = 0
	username = session["username"]
	c, conn = connection()
	data = c.execute("INSERT INTO photos (uid, link, description, likes, username) VALUES (%s, %s, %s, %s, %s)",(thwart(str(uid)),thwart(link),thwart(description), thwart(str(likes)), thwart(username)))
	conn.commit()
	c.close()
	conn.close()
	gc.collect()
	return url_for('news')

@app.route('/hello/', methods = ["GET", "POST"])
def hello():
	try:
		c, conn = connection()
		return "Hello"
	except Exception as e:
		return str(e)