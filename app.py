from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
import smtplib
import os
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from flask import abort
from sqlalchemy.orm import relationship


app = Flask(__name__)

# initializing CKEditor
ckeditor = CKEditor(app)

# setup for the smtp to send emails
my_email = "mgm.engineeringtie847@gmail.com"
gmail_password = os.environ.get("GMAIL_PASSWORD")

# configurations for sqlalchemy and the database
DB_PWD = os.environ.get("DB_PWD")
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{DB_PWD}@localhost/blog_db'
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
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Foreign key to link to the User (Parent)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Reference back to the User
    author = relationship("User", back_populates="posts")

    # One-to-Many relationship with Comemnt
    comments = relationship("Comment", back_populates="parent_post")


# User table model
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    # One-to-Many relationship with BlogPost
    posts = relationship("Post", back_populates="author")

    # One-to-Many relationship with Comment
    comments = relationship("Comment", back_populates="comment_author")


# The Comment model
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Foreign key linking the comment to a blog post
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    
    # Relationship back to the BlogPost
    parent_post = relationship("Post", back_populates="comments")
    
    # Foreign key linking the comment to a user (author)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship back to the User
    comment_author = relationship("User", back_populates="comments")


# admin decorator
def admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        # If id is not 1, return and abort with 403 error
        if current_user.is_authenticated and current_user.id != 1:
            return abort(403)
        # else proceed with the route function
        return function(*args, **kwargs)        
    return wrapper


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
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if the email is already in use
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already in use! Log in instead!', 'error')
            return redirect(url_for('login'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match! Please try again.', 'error')
            return redirect(url_for('signup'))
        
        # Create the new user if passwords match
        new_user = User(
            name = name,
            email = email,
            password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8),
        )

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log the user in
        login_user(new_user)

        return redirect(url_for('blogs'))
    return render_template("login.html", page_title='Sign Up', form_action=url_for('signup'))


@app.route("/post/<int:post_id>", methods=["POST", "GET"])
@login_required
def get_each_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        # Ensure the user is logged in
        if not current_user.is_authenticated:
            flash('You need to be logged in to comment.', 'danger')
            return redirect(url_for('login'))
        
        # Get comment content from the form
        comment_body = request.form.get('comment')

        # Create a new comment
        if comment_body:
            new_comment = Comment(
                body=comment_body,
                author_id=current_user.id,
                post_id=post_id,
                date_posted=datetime.utcnow()
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully!', 'success')
            return redirect(url_for('get_each_post', post_id=post_id))

    return render_template("post.html", post=post, comments=post.comments)


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
@admin_only
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
            author_id = current_user.id,
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
        post_to_edit.author_id = current_user.id
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
        return render_template("contact.html")

    return render_template("contact.html")


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


if __name__ == "__main__":
    print(app.url_map)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
