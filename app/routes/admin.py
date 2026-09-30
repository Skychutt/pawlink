from functools import wraps

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

from ..extensions import db
from ..models import AdoptionApplication, Pet, Species, User

admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin: abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/")
@admin_required
def index():
    stats={"users":User.query.count(),"pets":Pet.query.count(),"applications":AdoptionApplication.query.count(),"adopted":Pet.query.filter_by(status="adopted").count()}
    species_stats=db.session.query(Species.name,func.count(Pet.id)).outerjoin(Pet).group_by(Species.id).all()
    return render_template("admin/index.html",stats=stats,species_stats=species_stats,recent_users=User.query.order_by(User.created_at.desc()).limit(6).all(),pending=AdoptionApplication.query.filter_by(status="submitted").order_by(AdoptionApplication.created_at).limit(8).all())


@admin_bp.route("/pets")
@admin_required
def pets(): return render_template("admin/pets.html", pets=Pet.query.order_by(Pet.created_at.desc()).all())


@admin_bp.route("/users")
@admin_required
def users(): return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())
