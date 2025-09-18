# blueprints/auth/routes.py
import os
import random
import string
import uuid

from dotenv import load_dotenv
load_dotenv()
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Import your database and helper functions from a common module
from database.database import store_user_data,check_user_exists,get_user_password,get_user_role,get_user_first_name,update_accountUpdatedOn_column
from helpers import Password
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

# class Password:
#     def set_password(self,password):
#         self.password = generate_password_hash(password)
#         return self.password
#
#     def check_password(self,hashed_password, plain_password):
#         return check_password_hash(hashed_password, plain_password)

@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    #collect info from the login form
    #check if info in db
    if request.method == "POST":
        email = request.form.get("email")
        session['email']=email
        user_role = get_user_role(session['email'])
        session['role'] = user_role
        password = request.form.get("password")

        exists = check_user_exists(email)

        user_db_stored_password = get_user_password(email)
        pass_ob=Password()




        if exists:
            session['email']=email
            if pass_ob.check_password(user_db_stored_password,password) :
                first_name = get_user_first_name(email)
                logging.info(first_name)
                session['username'] = first_name
                session['toDashboard'] = True
                update_accountUpdatedOn_column(session['email'])
                return redirect(url_for("dashboard.dashboard"))
            else:
                return render_template("login.html", error="Invalid Password...Please try again!",email=session['email'])

        else:
            # otherwise show homepages
            return render_template("login.html",error="User does not exist.Please Sign Up first!")
    if request.method == "GET":
        return render_template("login.html",error="")


@auth_bp.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        exists = check_user_exists(email)
        if email:
            try:

                if exists:
                    return render_template("login.html", error="User Already Exists Here!")

                else:

                    first_name = request.form.get("first_name")
                    last_name = request.form.get("last_name")
                    email = request.form.get("email")
                    password = request.form.get("password")
                    session['signup_first_name']=first_name
                    session['signup_last_name']=last_name
                    session['signup_email']=email
                    session['signup_password']=password

                    otp = ''.join(random.choices(string.digits, k=6))
                    session['otp']=otp
                    logging.info("OTP:",otp)

                    otp_expiry = datetime.now() + timedelta(seconds=50)
                    sender_email = "chanurakarunanayake12@gmail.com"
                    app_password = os.getenv("GMAIL_APP_PASSWORD")

                    # Build email
                    message = MIMEMultipart()
                    message["From"] = sender_email
                    message["To"] = session.get('signup_email')
                    message["Subject"] = "Your OTP Code"

                    body = f"Your verification code is: {otp}"
                    message.attach(MIMEText(body, "plain"))
                    body = f"Your verification code is: {otp}"
                    message.attach(MIMEText(body, "plain"))
                    try:
                        with smtplib.SMTP("smtp.gmail.com", 587) as server:
                            server.starttls()
                            server.login(sender_email, app_password)
                            server.sendmail(sender_email, session.get('signup_email'), message.as_string())
                            session["otp_sent_message"] = True
                            return redirect(url_for("auth.verify_email"))

                    except Exception as e:
                          logging.error(f"Error sending OTP: {e}")
            except Exception as e:
                print(e)
        else:
            return render_template("signup.html", error="Please enter valid details!")

    if request.method == "GET":
        return render_template("signup.html")
    return render_template("signup.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop("username", None)
        session.pop("email", None)
        session.pop("toDashboard", False)
        session.clear()
        return redirect(url_for("auth.login"))
    return redirect(url_for("dashboard.dashboard"))

@auth_bp.route("/email_verification", methods=["POST", "GET"])
def verify_email():
    if request.method == "GET":
        return render_template("verify_email.html")
    if request.method == "POST":
        otp_password = request.form.get("otp_password")
        if session.get("otp_sent_message"):
            if otp_password==session.get('otp'):
                session['otp'] = None

                first_name = session.get('signup_first_name')
                last_name = session.get('signup_last_name')
                email = session.get('signup_email')
                password = session.get('signup_password')

                logging.info("📌 DEBUG Signup values:", first_name, last_name, email, password)

                pass_obj = Password()
                encrypt_password = pass_obj.set_password(password)

                # fernet_key = Fernet.generate_key()
                # fernet_key_str = fernet_key.decode()
                unique_id = str(uuid.uuid4())
                session['log_data_unique_id'] = unique_id

                sri_lanka_tz = ZoneInfo("Asia/Colombo")
                local_time = datetime.now(sri_lanka_tz)
                signup_status = True
                account_status = True

                store_user_data(first_name, last_name, email, encrypt_password, unique_id, local_time, signup_status,
                                account_status, "user")

                session["username"] = first_name
                return redirect(url_for("auth.login"))

            else:
                session['otp'] = None
                return render_template("verify_email.html", error="Invalid OTP...Please try again!")
        else:
            return redirect(url_for("auth.signup"))



