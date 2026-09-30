# Python-s3-rds


# Python S3 RDS Flask Application

A Flask-based application integrated with **MySQL (RDS)** and **AWS S3** for user authentication and profile/avatar storage.

## Project Structure

```text
Python-s3-rds/
│
├── __pycache__/
├── templates/
│
├── .env
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── Dockerfile
├── README.md
└── requirements.txt



## Database Setup

### 1. Create Database

```sql
CREATE DATABASE flask_auth;


USE flask_auth;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    avatar_url TEXT
);




