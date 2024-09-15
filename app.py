from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import smtplib
import os
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user


app = Flask(__name__)

# initializing CKEditor
ckeditor = CKEditor(app)

# setup for the smtp to send emails
my_email = "mgm.engineeringtie847@gmail.com"
gmail_password = os.environ.get("GMAIL_PASSWORD")

# configurations for sqlalchemy and the database
DB_PWD = os.environ.get("DB_PWD")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{DB_PWD}@localhost/blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) #  creating the db object for managing CRUD operations


# LoginManager configurations
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.environ.get("SECRET_KEY")


# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))


# The model for the posts (table in database blog)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# User table model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


@app.route("/", methods=['GET'])
def blogs():
    # Get the page number from the URL, default to 1 if not provided
    page = request.args.get('page', 1, type=int)

    # number of posts per page
    per_page = 4

    # Querying the database to get the posts for the current page
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # next and previous page URLs
    next_url = url_for('blogs', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('blogs', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', posts=posts.items, next_url=next_url, prev_url=prev_url)



@app.route('/blogss', methods=['GET'])
def blogss():
    # Get the page number from the URL, default to 1 if not provided
    page = request.args.get('page', 1, type=int)

    # Set the number of posts per page (for pagination, excluding the carousel)
    per_page = 2

    # Query the database to get the first 3 posts for the carousel
    latest_posts = Post.query.order_by(Post.date.desc()).limit(3).all()

    # For pagination, order by date first, then offset and paginate
    query = Post.query.order_by(Post.date.desc())

    # Apply offset to skip the first 3 posts and paginate
    paginated_posts = query.offset(3).paginate(page=page, per_page=per_page, error_out=False)

    # Get next and previous page URLs for pagination
    next_url = url_for('blogss', page=paginated_posts.next_num) if paginated_posts.has_next else None
    prev_url = url_for('blogss', page=paginated_posts.prev_num) if paginated_posts.has_prev else None

    return render_template(
        'carousel.html',
        posts=paginated_posts.items,
        latest_posts=latest_posts,
        next_url=next_url,
        prev_url=prev_url
    )




@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email = request.form.get("email")).first()
        if user:
            password_match = check_password_hash(user.password, request.form.get("password"))
            if password_match:
                flash('Successfully logged in!', 'success')
                login_user(user)
                return redirect(url_for('blogs'))
            else:
                flash('Incorrect Password!', 'error')
                return redirect(url_for("login"))
        else:
            flash('Email does not exist.Please Try Again!', 'error')
            return redirect(url_for('login'))
    return render_template("login.html", page_title='Login', form_action=url_for('login'))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already in use! Log in instead!', 'error')
            return redirect(url_for('login'))
        else:
            new_user = User(
                name = request.form.get("username"),
                email = email,
                password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8),
                # confirm_password = request.form.get("confirm_password")
            )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('blogs'))
    return render_template("login.html", page_title='Sign Up', form_action=url_for('signup'))


@app.route("/post/<int:post_id>")
@login_required
def get_each_post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", post=post)


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def view_dashboard():
    posts = Post.query.all()

    return render_template("dashboard.html", posts=posts)


@app.route("/new-post", methods=["POST", "GET"])
@login_required
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
    return render_template("create-edit-post.html")


@app.route('/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)

    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('view_dashboard'))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/edit-post/<int:post_id>", methods=["POST", "GET"])
@login_required
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

    return render_template("create-edit-post.html", post_to_edit=post_to_edit)


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/contact", methods=['POST', 'GET'])
@login_required
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
