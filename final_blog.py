#!user/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session, g, flash
import sqlite3
import time


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
    flash('You are now logged in!')
    if session['logged_in'] == False:
        return redirect('/login')
    else:
        cur = g.db.execute('SELECT id, title, content, date FROM entries ORDER BY id')
        entries = [dict(id=row[0], title=row[1], post_date=row[3]) for row in cur.fetchall()]

        return render_template('dashboard.html', entries=entries)

@app.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
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

@app.route('/add', methods = ['GET', 'POST'])
def add():
    cur_date = time.strftime("%c")
    if session['logged_in'] == False:
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('add.html')

    if request.method == 'POST':
        g.db.execute('INSERT INTO entries (title, content, date) VALUES (?, ?, ?)', [request.form['add_title'],
                                                                                           request.form['add_content'],
                                                                                           cur_date])
        g.db.commit()
        return redirect('/dashboard')

@app.route('/view_blogs', methods = ['GET'])
def view_blogs():
    if session['logged_in'] == False:
        return redirect('/login')
    cur = g.db.execute('SELECT id, title, content, date FROM entries ORDER BY date ASC, id ASC')
    entries = [dict(id=row[0], title=row[1], content=row[2], date=row[3]) for row in cur.fetchall()]

    return render_template('view_blogs.html', entries = entries)


@app.route('/delete', methods = ['POST'])
def delete():
    print 'Delete page'







if __name__ == "__main__":
    app.run()
    connect_db()