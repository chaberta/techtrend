import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging
import sys
# Function to get a database connection.
# This function connects to database with the name `database.db`
connection_count = 0


def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count = connection_count+1
    return connection

# Function to get a post using its ID


def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application


@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown


@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        log_message(
            'Article with id "{id}" do not exist'.format(id=post_id))
        return render_template('404.html'), 404
    else:
        log_message('Article "{title}" retrieved!'.format(title=post['title']))
        return render_template('post.html', post=post)

# Define the About Us page


@app.route('/about')
def about():
    log_message('About us')
    return render_template('about.html')

# Define the post creation functionality


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            log_message('Article "{title}" is created'.format(title=title))
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/metrics')
def metrics():
    connection_count = get_db_connection()
    posts_count = connection_count.execute('SELECT * FROM posts').fetchall()
    connection_count.close()
    posts_value = len(posts_count)
    response = {"post_count": posts_value,
                "db_connection_count": connection_count}

    return response


def log_message(msg):
    app.logger.info('{time} | {message}'.format(
        time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), message=msg))


# start the application on port 3111
if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    handlers = [stderr_handler, stdout_handler]
    format_output = '%(levelname)s: %(name)-2s - [%(asctime)s] - %(message)s'
    logging.basicConfig(format=format_output,
                        level=logging.DEBUG, handlers=handlers)
    app.run(host='0.0.0.0', port='3111')

