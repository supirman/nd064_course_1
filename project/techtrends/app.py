import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
from os import sys

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection(count=True):
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    if count: increment_connection_count(connection)
    return connection


def increment_connection_count(connection):
    connection.execute('UPDATE count SET value = value + 1 WHERE key = "db_connection_count"')
    connection.commit()

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
    app.logger.info('Homepage request successfull')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error('A non-existing article is accessed and a 404 page returned')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "{}" retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us page request successfull')
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
            app.logger.info('Create new page "{}" successfull'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/healthz')
def healthcheck():
    connection = get_db_connection(False)
    # check posts table if exist https://stackoverflow.com/a/1604121/773307
    result = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'").fetchone()
    if result:
        response = app.response_class(
                response=json.dumps({"result":"OK - healthy"}),
                status=200,
                mimetype='application/json'
        )
        app.logger.info('Status request successfull')
    else:
        response = app.response_class(
                response=json.dumps({"result":"ERROR - unhealthy"}),
                status=500,
                mimetype='application/json'
        ) 
        app.logger.error('Database connection error')
    
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = 0
    db_connection_count = 0
    post_count_row = connection.execute('SELECT count(id) FROM posts').fetchone()
    if post_count_row is not None:
        post_count = post_count_row[0]
    db_connection_count_row = connection.execute('SELECT value FROM count WHERE key = "db_connection_count"').fetchone()
    if db_connection_count_row is not None:
        db_connection_count = db_connection_count_row[0]
    
    response = app.response_class(
            response=json.dumps({"db_connection_count":db_connection_count,"post_count":post_count}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response


# start the application on port 3111
if __name__ == "__main__":
    logger = logging.getLogger("__name__")
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    handlers = [stderr_handler, stdout_handler]

    logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s, %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d, %H:%M:%S', handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
