from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import boto3
from config import Config
import uuid

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
    region_name=app.config["AWS_REGION"]
)

# ===================== SIGNUP =====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        file = request.files["avatar"]

        filename = str(uuid.uuid4()) + file.filename

        s3.upload_fileobj(
                file,
                app.config["AWS_BUCKET_NAME"],
                filename
        )


        avatar_url = f"https://{app.config['AWS_BUCKET_NAME']}.s3.amazonaws.com/{filename}"

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(name,email,password,avatar_url) VALUES(%s,%s,%s,%s)",
            (name, email, password, avatar_url)
        )
        mysql.connection.commit()
        cur.close()

        return redirect("/signin")

    return render_template("signup.html")


# ===================== SIGNIN =====================
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["avatar"] = user[4]
            return redirect("/home")

        return "Invalid Credentials"

    return render_template("signin.html")


# ===================== HOME =====================
@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/signin")

    return render_template(
        "home.html",
        name=session["name"],
        avatar=session["avatar"]
    )


# ===================== LOGOUT =====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/signin")


if __name__ == "__main__":
    app.run(debug=True)
