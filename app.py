from flask import Flask, render_template, request, jsonify
from datetime import datetime


app = Flask(__name__)


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

        # Basic validation
        if not name or not email or not message:
            return jsonify({"error": "All fields are required!"}), 400

        print(name, email, message)
        return jsonify({"message": "Message successfully sent"}), 200

    return render_template("contact.html")


def get_current_year():
    return datetime.now().year


if __name__ == "__main__":
    app.run(debug=True)
