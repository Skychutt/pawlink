from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from ..extensions import db
from ..forms import LoginForm, RegisterForm
from ..models import User

auth_bp = Blueprint("auth", __name__)


def _safe_next(target):
    base = urlparse(request.host_url); test = urlparse(urljoin(request.host_url, target or ""))
    return test.netloc == base.netloc and test.scheme in {"http", "https"}


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        account = form.account.data.strip()
        user = User.query.filter(or_(User.username == account, User.email == account)).first()
        if not user or not user.check_password(form.password.data): flash("账号或密码不正确", "error")
        elif not user.is_active_account: flash("该账号已被停用，请联系管理员", "error")
        else:
            remember = bool(form.remember.data)
            login_user(user, remember=remember)
            session.permanent = remember
            target = request.args.get("next")
            flash(f"欢迎回来，{user.display_name}", "success")
            return redirect(target if _safe_next(target) else url_for("dashboard.index"))
    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated: return redirect(url_for("dashboard.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first(): form.username.errors.append("用户名已存在")
        elif User.query.filter_by(email=form.email.data.strip().lower()).first(): form.email.errors.append("邮箱已注册")
        else:
            user = User(username=form.username.data.strip(), display_name=form.display_name.data.strip(), email=form.email.data.strip().lower(), phone=form.phone.data.strip(), city=form.city.data.strip())
            user.set_password(form.password.data); db.session.add(user); db.session.commit(); login_user(user)
            flash("账号创建成功，欢迎加入暖爪", "success"); return redirect(url_for("dashboard.index"))
    return render_template("auth/register.html", form=form)


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated: logout_user()
    flash("你已安全退出", "success"); return redirect(url_for("main.index"))
