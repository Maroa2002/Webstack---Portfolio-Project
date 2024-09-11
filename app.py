from flask import Flask, render_template, request, jsonify
from datetime import datetime
import smtplib
import os


app = Flask(__name__)
my_email = "mgm.engineeringtie847@gmail.com"
gmail_password = os.environ.get("GMAIL_PASSWORD")


# current_year = get_current_year()


@app.route("/")
def home():
    return render_template("index.html")


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
    app.run(debug=True)
