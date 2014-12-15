from flask import render_template

from blog import app
from database import session
from models import Post


import mistune
from flask import request, redirect, url_for


from flask import flash
from flask.ext.login import login_user, logout_user, login_required # methods and a decorator
from werkzeug.security import check_password_hash
from models import User

app.jinja_env.filters.setdefault('markdown', mistune.markdown)

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    """Logs out the user, redirects to the home page"""
    logout_user()
    return redirect(url_for('posts'))


# @app.route("/")
# def posts():
#     posts = session.query(Post)
#     posts = posts.order_by(Post.datetime.desc())
#     posts = posts.all()
#     return render_template("posts.html",
#         posts=posts
#     )


@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by  # The index of the first item that we should see
    end = start + paginate_by  # The index of the last item that we should see

    total_pages = (count - 1) / paginate_by + 1  # The total number of pages of content
    has_next = page_index < total_pages - 1 # Whether there is a page after our current one
    has_prev = page_index > 0  # Whether there is a page before our current one


    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
    )



@app.route("/post/<int:id>")
def post(id):
    post = session.query(Post).get(id)
    post.content=mistune.markdown(post.content)
    # posts = posts.order_by(Post.datetime.desc())
    # post = posts[post_id]

    return render_template("post.html",
        post=post,
    )


@app.route("/post/<int:id>/edit")
@login_required
def edit_post_get(id):
    post = session.query(Post).get(id)
#    post.content=mistune.markdown(request.form["content"])

    return render_template("edit_post.html",
        post_title = post.title,
        post_content = post.content,
 )


@app.route("/post/<int:id>/delete")
@login_required
def delete_post_get(id):
    post = session.query(Post).get(id)
    session.delete(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<int:id>/edit", methods=["POST"])
@login_required
def edit_post_post(id):

    post = session.query(Post).get(id)

#    post1 = Post(
    post.title=request.form["title"]
#    post.content=mistune.markdown(request.form["content"])
    post.content=request.form["content"]

#    )
#    session.add(post1)
    session.commit()
    return redirect(url_for("posts"))



@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")


@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=request.form["content"],
        )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))


