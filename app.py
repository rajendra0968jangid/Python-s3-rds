from flask import Flask, render_template, request, redirect, session
import pymysql
import boto3
import uuid
import os

from dotenv import load_dotenv


# =====================================================
# LOAD .ENV
# =====================================================

load_dotenv()


# =====================================================
# FLASK APP
# =====================================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")


# =====================================================
# ENVIRONMENT VARIABLES
# =====================================================

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


# =====================================================
# MYSQL CONNECTION FUNCTION
# =====================================================

def get_db_connection():

    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.Cursor,
        autocommit=False
    )


# =====================================================
# S3 CLIENT
# =====================================================

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# =====================================================
# TEST ROUTE
# =====================================================

@app.route("/")
def index():

    return redirect("/signin")


# =====================================================
# SIGNUP
# =====================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        file = request.files.get("avatar")


        # Validate fields

        if not name or not email or not password:
            return "Name, email and password are required"


        # Validate avatar

        if not file or file.filename == "":
            return "Avatar is required"


        # =================================================
        # GENERATE UNIQUE FILE NAME
        # =================================================

        filename = f"{uuid.uuid4()}_{file.filename}"


        # =================================================
        # UPLOAD TO S3
        # =================================================

        try:

            s3.upload_fileobj(
                file,
                AWS_BUCKET_NAME,
                filename
            )

        except Exception as e:

            return f"S3 Upload Error: {str(e)}"


        # =================================================
        # S3 URL
        # =================================================

        avatar_url = (
            f"https://{AWS_BUCKET_NAME}.s3."
            f"{AWS_REGION}.amazonaws.com/{filename}"
        )


        # =================================================
        # SAVE USER TO MYSQL
        # =================================================

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password, avatar_url)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    name,
                    email,
                    password,
                    avatar_url
                )
            )

            connection.commit()

        except pymysql.err.IntegrityError:

            if connection:
                connection.rollback()

            return "Email already exists"

        except Exception as e:

            if connection:
                connection.rollback()

            return f"MySQL Error: {str(e)}"

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


        return redirect("/signin")


    return render_template("signup.html")


# =====================================================
# SIGNIN
# =====================================================

@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")


        # =================================================
        # GET USER FROM MYSQL
        # =================================================

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id, name, email, password, avatar_url
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

        except Exception as e:

            return f"MySQL Error: {str(e)}"

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


        # =================================================
        # CHECK PASSWORD
        # =================================================

        if user and user[3] == password:

            session["user_id"] = user[0]
            session["name"] = user[1]
            session["avatar"] = user[4]

            return redirect("/home")


        return "Invalid Credentials"


    return render_template("signin.html")


# =====================================================
# HOME
# =====================================================

@app.route("/home")
def home():

    if "user_id" not in session:

        return redirect("/signin")


    return render_template(
        "home.html",
        name=session["name"],
        avatar=session["avatar"]
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/signin")


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )

