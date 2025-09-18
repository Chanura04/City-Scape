from flask import Flask, render_template, request
import os, glob, uuid

from blueprints.home import home_bp
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.result_page_1 import result_page_1_bp

def clear_session_files():
    for file in glob.glob("flask_session/*"):
        os.remove(file)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "default-secret-key")

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(home_bp, url_prefix='/')
    app.register_blueprint(result_page_1_bp, url_prefix='/result_page_one')

    # app.register_blueprint(view_voting_card_bp, url_prefix='/voting_card')

    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    # app.register_blueprint(api_details_bp, url_prefix='/api_details')

    # Add other configurations if needed
    app.config["SESSION_RESET_TOKEN"] = str(uuid.uuid4())
    clear_session_files()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)




#     (.venv) PS C:\Github Projects\Data-Compass> docker build -t chanura04/data-compass-web:latest .
# (.venv) PS C:\Github Projects\Data-Compass> docker login
# (.venv) PS C:\Github Projects\Data-Compass> docker push chanura04/data-compass-web:latest