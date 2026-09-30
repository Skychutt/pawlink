import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from .extensions import csrf, db, login_manager


def create_app(test_config=None):
    # 固定从项目根目录加载 .env，避免工作目录变化导致读不到密钥
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
    app = Flask(__name__, instance_relative_config=True)
    default_database = "sqlite:///" + os.path.join(
        app.instance_path, "pawlink.db"
    )
    cookie_secure = os.environ.get("COOKIE_SECURE", "0") == "1"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "pawlink-dev-secret-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", default_database),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_TIME_LIMIT=None,
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=cookie_secure,
        REMEMBER_COOKIE_DURATION=timedelta(days=30),
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_SECURE=cookie_secure,
        DEEPSEEK_API_KEY=os.environ.get("DEEPSEEK_API_KEY", "").strip(),
        DEEPSEEK_API_URL=os.environ.get(
            "DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions"
        ).strip(),
        DEEPSEEK_MODEL=os.environ.get(
            "DEEPSEEK_MODEL", "deepseek-v4-flash"
        ).strip(),
        DEEPSEEK_TIMEOUT=30,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录后再继续"
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.admin import admin_bp
    from .routes.api import api_bp
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.pets import pets_bp
    from .routes.shelter import shelter_bp
    from .routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(pets_bp, url_prefix="/pets")
    app.register_blueprint(shelter_bp, url_prefix="/shelter")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "object-src 'none'; frame-ancestors 'self'",
        )
        return response

    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith("/api/"):
            return jsonify(ok=False, message="你没有执行此操作的权限"), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify(ok=False, message="请求的资源不存在"), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify(ok=False, message="服务器暂时无法处理请求"), 500
        return render_template("errors/500.html"), 500

    from .seed import register_commands

    register_commands(app)

    # 为已有 SQLite 数据库补建新增表，不删除或覆盖现有数据。
    with app.app_context():
        db.create_all()

    return app
