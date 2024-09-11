from flask import Flask, render_template, request, jsonify
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


# current_year = get_current_year()


@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/post")
def post():
    return render_template("post.html")


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


def get_current_year():
    return datetime.now().year


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
