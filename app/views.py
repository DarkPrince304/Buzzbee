from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from app import app

@app.route('/')
@app.route('/index/')
@app.route('/home/')
def index():
	return render_template('home.html')

@app.route('/hello/')
def hello():
	return "Hello"