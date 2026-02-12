import os

class Config:
    SECRET_KEY = "your_secret_key"

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "your_mysql_password"
    MYSQL_DB = "flask_auth"

    # AWS S3
    AWS_ACCESS_KEY_ID = "your_access_key"
    AWS_SECRET_ACCESS_KEY = "your_secret_key"
    AWS_BUCKET_NAME = "your_bucket_name"
    AWS_REGION = "ap-south-1"
