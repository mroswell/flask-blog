from flask import render_template

from blog import app
from database import session
from models import Post


import mistune
from flask import request, redirect, url_for

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
        total_pages=total_pages
    )


@app.route("/post/add", methods=["GET"])
def add_post_get():
    return render_template("add_post.html")


@app.route("/post/add", methods=["POST"])
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))
