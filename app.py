from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import smtplib
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# setup for the smtp to send emails
my_email = "mgm.engineeringtie847@gmail.com"
gmail_password = os.environ.get("GMAIL_PASSWORD")

# configurations for sqlalchemy and the database
DB_PWD = os.environ.get("DB_PWD")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{DB_PWD}@localhost/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #  creating the db object for managing CRUD operations

# The model for the posts (table in database blog)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


@app.route("/")
def retrieve_all_posts():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/post/<int:post_id>")
def get_each_post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", post=post)


@app.route("/dashboard", methods=["POST", "GET"])
def view_dashboard():
    posts = Post.query.all()

    return render_template("dashboard.html", posts=posts)


@app.route("/new-post", methods=["POST", "GET"])
def create_new_post():
    if request.method == "POST":
        new_post = Post(
            title = request.form.get("title"),
            subtitle = request.form.get("subtitle"),
            date = get_current_date(),
            body = request.form.get("body"),
            author = request.form.get("author"),
            img_url = request.form.get("img_url"),
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('view_dashboard'))
    return render_template("new-post.html")


@app.route('/delete-post/<int:post_id>')
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)

    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('view_dashboard'))


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
def edit_current_post(post_id):
    post_to_edit = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post_to_edit.title = request.form.get("title")
        post_to_edit.subtitle = request.form.get("subtitle")
        post_to_edit.body = request.form.get("body")
        post_to_edit.author = request.form.get("author")
        post_to_edit.img_url = request.form.get("img_url")

        db.session.commit()

        return redirect(url_for('get_each_post', post_id=post_to_edit.id))

    return render_template("edit-post.html", post_to_edit=post_to_edit)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        name = request.form.get("username")
        email = request.form.get("email")
        message = request.form.get("message")

        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=gmail_password)
            connection.sendmail(
                from_addr=my_email,
                to_addrs=my_email,
                msg="Subject:Contact\n\n{}\n\n{}\n\n{}".format(name, email, message)
        )

        # # Basic validation
        # if not name or not email or not message:
        #     return jsonify({"error": "All fields are required!"}), 400

        # return jsonify({"message": "Message successfully sent"}), 200
        return render_template("contact.html")

    return render_template("contact.html")


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
