from flask import Flask
from flask_cors import CORS
from app.core.config import settings

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET

    CORS(app, origins=settings.CORS_ORIGINS)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
