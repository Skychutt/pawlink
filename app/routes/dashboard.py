from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..forms import ProfileForm

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    tab = request.args.get("tab", "applications")
    applications = sorted(current_user.applications, key=lambda x: x.created_at, reverse=True)
    appointments = sorted(current_user.appointments, key=lambda x: x.scheduled_at)
    favorites = sorted(current_user.favorites, key=lambda x: x.created_at, reverse=True)
    signups = sorted(current_user.volunteer_signups, key=lambda x: x.created_at, reverse=True)
    notes = sorted(current_user.notifications, key=lambda x: x.created_at, reverse=True)[:10]
    return render_template("dashboard/index.html", tab=tab, applications=applications, appointments=appointments, favorites=favorites, signups=signups, notifications=notes)


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        for field in ["display_name","phone","city","bio","avatar_color"]: setattr(current_user, field, getattr(form, field).data.strip() if isinstance(getattr(form, field).data, str) else getattr(form, field).data)
        db.session.commit(); flash("个人资料已保存", "success"); return redirect(url_for("dashboard.profile"))
    return render_template("dashboard/profile.html", form=form)
