from flask import Flask
from flask_cors import CORS
from app.core.jwt import jwt
from app.core.config import settings
from app.api.auth.routes import auth_bp
from app.api.productos.routes import productos_bp

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_EXPIRATION

    CORS(app, origins=settings.CORS_ORIGINS)
    jwt.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
