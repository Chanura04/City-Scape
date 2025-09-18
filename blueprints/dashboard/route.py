import uuid
import logging
from flask import Blueprint, render_template,session,flash, redirect, url_for, request
from database.database import store_log_data_db,get_current_user_unique_id
from helpers import current_local_time
from datetime import datetime
from zoneinfo import ZoneInfo
dashboard_bp=Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')


@dashboard_bp.route("/main",methods=["GET","POST"])
def dashboard():
    # if session.get("reset_token") != current_app.config["SESSION_RESET_TOKEN"]:
    #     session.clear()
    #     session["reset_token"] = current_app.config["SESSION_RESET_TOKEN"]

    if not session.get("username"):
        return redirect(url_for("auth.login"))


    if request.method == "POST":
        session['toDashboard']=True
        user_role = session.get('role', 'user')
        country_or_city_input = request.form.get("country_or_city_input")
        # sri_lanka_tz = ZoneInfo("Asia/Colombo")
        unique_id = get_current_user_unique_id(session.get('email'))
        # local_time = datetime.now(sri_lanka_tz)
        local_time =  current_local_time()
        session['current_query_time'] = local_time

        store_log_data_db(
            city_or_country=country_or_city_input,
            local_time=local_time,
            email=session.get('email'),
            unique_id=unique_id,
            query_status="User Input Store to Database"
        )
        logging.info(unique_id)
        # return render_template("result_page.html" ,user_input=country_or_city_input,role=user_role )
        return redirect(url_for("result_page_1.show_page_one_data",city_name=country_or_city_input))


    if request.method == "GET":
        user_role = session.get('role', 'user')
        return render_template("dashboard.html" ,username=session.get('username'), role=user_role ,error="Please enter a valid city name!")


