from functools import wraps

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from ..extensions import db
from ..models import AdoptionApplication, Pet, VisitAppointment

shelter_bp = Blueprint("shelter", __name__)


def shelter_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_shelter: abort(403)
        return view(*args, **kwargs)
    return wrapped


@shelter_bp.route("/")
@shelter_required
def index():
    query = Pet.query if current_user.is_admin else Pet.query.filter_by(shelter_id=current_user.id)
    pets = query.order_by(Pet.created_at.desc()).all(); pet_ids = [p.id for p in pets] or [0]
    applications = AdoptionApplication.query.filter(AdoptionApplication.pet_id.in_(pet_ids)).order_by(AdoptionApplication.created_at.desc()).all()
    appointments = VisitAppointment.query.filter(VisitAppointment.pet_id.in_(pet_ids)).order_by(VisitAppointment.scheduled_at).limit(8).all()
    stats = {"pets":len(pets),"available":sum(p.status=="available" for p in pets),"applications":sum(a.status=="submitted" for a in applications),"home":sum(p.status=="adopted" for p in pets)}
    return render_template("shelter/index.html", pets=pets, applications=applications, appointments=appointments, stats=stats)
