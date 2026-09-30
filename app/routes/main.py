from datetime import datetime

from flask import Blueprint, render_template

from ..models import Announcement, AdoptionApplication, Pet, Species, User, VolunteerActivity

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    featured = Pet.query.filter(Pet.status.in_(["available", "recovery"])).order_by(Pet.featured.desc(), Pet.created_at.desc()).limit(6).all()
    species = Species.query.order_by(Species.id).all()
    announcement = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).first()
    volunteer = VolunteerActivity.query.filter(VolunteerActivity.starts_at >= datetime.now()).order_by(VolunteerActivity.starts_at).limit(2).all()
    stats = {"pets": Pet.query.count(), "home": Pet.query.filter_by(status="adopted").count(), "members": User.query.filter_by(is_active_account=True).count(), "applications": AdoptionApplication.query.count()}
    return render_template("index.html", featured=featured, species=species, announcement=announcement, volunteer=volunteer, stats=stats)


@main_bp.route("/about")
def about(): return render_template("about.html")


@main_bp.route("/volunteer")
def volunteer():
    activities = VolunteerActivity.query.order_by(VolunteerActivity.starts_at.asc()).all()
    return render_template("volunteer.html", activities=activities)
