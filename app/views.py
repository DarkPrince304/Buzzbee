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
				conn.commit()
				c.close()
				conn.close()
				gc.collect()
				session["logged_in"] = True
				session["username"] = username
				return render_template("news.html", username = session["username"], loggedIn = session["logged_in"])
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
			print "Hello"
			username = formLog.username.data
			password = formLog.password.data
			print username, password
			c, conn = connection()
			data = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))
			data = c.fetchone()[2]
			print "hello",data
			print "Hello"
			if sha256_crypt.verify(password, data):
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
		data = c.execute("SELECT username FROM users")
		data = c.fetchall()
		users = []
		for i in data:
			users.append(str(i).strip("(),'"))
		return render_template("news.html", entries = users, username = session["username"], loggedIn = session["logged_in"])
	except Exception as e:
		return str(e)

@app.route('/logout/')
def logout():
	session['username']=''
	session['logged_in']=False
	return redirect(url_for("index"))

@app.route('/profile/')
def profile():
	return render_template("profile.html", username = session["username"])

@app.route('/uploadpic/')
def uploadpic():
	return render_template("uploadpic.html", username = session["username"], loggedIn = session["logged_in"])

@app.route('/hello/', methods = ["GET", "POST"])
def hello():
	try:
		c, conn = connection()
		return "Hello"
	except Exception as e:
		return str(e)
