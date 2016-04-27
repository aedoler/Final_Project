#!user/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session, g, url_for, flash
import sqlite3


DATABASE = 'blog.db'
DEBUG = True
SECRET_KEY = 'secret_key'
USERNAME = 'admin'
PASSWORD = 'password'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def get_db():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def hello_world():

    return redirect('/login')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect('/dashboard')

    return render_template('login.html', error=error)

@app.route('/dashboard', methods = ['GET'])
def dashboard():
    if session['logged_in'] == False:
        return redirect('/login')
    else:
        cur = g.db.execute('SELECT id, title, content, date FROM entries ORDER BY id')
        entries = [dict(id=row[0], title=row[1], post_date=row[3]) for row in cur.fetchall()]

        return render_template('dashboard.html', entries=entries)

@app.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    print id
    if session['logged_in'] == False:
        return redirect('/login')
    else:
        if request.method == 'GET':
            cur = g.db.execute('SELECT id, title, content FROM entries WHERE id = ?', id)
            entries = [dict(id=row[0], title=row[1], content=row[2]) for row in cur.fetchall()]
            return render_template('edit.html', entries=entries)
        elif request.method == 'POST':
            g.db.execute('UPDATE entries SET content = ?, title = ? WHERE id = ?', [request.form['edit_blog'],
                                                                                       request.form['blog_title'],
                                                                                       id])
            g.db.commit()
            return redirect('/dashboard')


if __name__ == "__main__":
    app.run()
    connect_db()