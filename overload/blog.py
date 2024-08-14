from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file, session
)

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from overload.auth import login_required
from overload.db import get_db

import markdown
from markupsafe import Markup
from bleach import clean
import os

from overload.image_processing import find_and_replace_image_urls

bp = Blueprint("blog",__name__)


@bp.route("/")
def index():
    db = get_db()
    posts=db.execute(
        """ SELECT p.id, title, body, created, author_id, username
        FROM post p JOIN user u ON p.author_id = u.id
        ORDER BY created DESC
        """
    ).fetchall()
    htmlposts = []
    for post in posts:
        post = dict(post)
        post["title"] = post["title"]
        post["body"] = Markup(markdown.markdown(clean(post["body"]),extensions=["nl2br"]))
        htmlposts.append(post)

    return render_template("blog/index.html", posts=htmlposts)


@bp.route("/create", methods=("GET","POST"))
@login_required(5)
def create():
    if request.method == 'POST':
        title = clean(request.form['title'])
        body = clean(request.form['body'])
        body = find_and_replace_image_urls(body)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, Markup(body), g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id'] and g.user["authority"] < 10:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required(5)
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = clean(request.form['title'])
        body = clean(request.form['body'])
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required(5)
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route("/posts/<int:id>", methods=("GET",))
def post_page(id): # This url returns a page that contains just a single post.
    post = dict(get_post(id, False))
    post["body"] = Markup(markdown.markdown(clean(post["body"]),extensions=["nl2br"]))

    return render_template("blog/post.html",post=post)


@bp.route("/image_upload", methods=("GET","POST",))
@login_required(5)
def image_upload(): # This endpoint allows you to upload images, 
    if request.method == "POST":
        ALLOWED_EXTENSTION = {"png","jpg","jpeg","gif"}
        files = request.files
        form = request.form

        num = 1
        error = []
        db = get_db()
        while True:
            if f"image_{num + 1}" not in files:
                break
            image = files[f"image_{num}"]
            name = form[f"name_{num}"]
            alt_text = form[f"alt_{num}"]
            try:
                file_extension = image.filename.rsplit(".",1)[1].lower()

            except:
                file_extension = None
            if image.filename == "":
                error.append(f"No file for upload {num}.")

                num += 1
                continue
            if file_extension not in ALLOWED_EXTENSTION:
                error.append(f"File extenstion {file_extension} for upload {num} not allowed.")
                num += 1
                continue
            if name == "":
                error.append(f"No name for upload {num}.")

                num += 1
                continue
                
            filename = secure_filename(name + "." + file_extension)
            try:

                db.execute("""
                INSERT INTO image (name,alt_text,uploader_id) VALUES (?,?,?)
                """,(filename,alt_text,session.get("user_id")))
                db.commit()

                image.save(os.path.join(current_app.config["IMAGE_UPLOAD"],filename))

            except db.IntegrityError:
                error.append(f"Upload {num} name {filename} already exists.")

            num += 1

        if error == []:
            pass
        else:
            for err in error:
                flash(err)
    
    return render_template("blog/image_upload.html")

@bp.route("/image/<int:id>")
def get_image(id):
    db = get_db()
    image = db.execute(f"SELECT * FROM image WHERE id={id}").fetchone()
    return send_file(os.path.join(current_app.config["IMAGE_UPLOAD"], image["name"]))

@bp.route("/images", methods=("GET",))
@login_required(5)
def image_gallery():
    db = get_db()
    images = db.execute("SELECT * FROM image").fetchall()
    images = [dict(image) for image in images]
    return render_template("blog/image_gallery.html",images=images)

@bp.route("/image/name/<string:name>")
def get_image_by_name(name):
    return send_file(os.path.join(current_app.config["IMAGE_UPLOAD"], name))
