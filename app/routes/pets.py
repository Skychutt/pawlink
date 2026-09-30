from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from ..extensions import db
from ..forms import PetForm
from ..models import AdoptionApplication, Favorite, Pet, Species

pets_bp = Blueprint("pets", __name__)


@pets_bp.route("/")
def index():
    query = Pet.query
    keyword = request.args.get("q", "").strip(); species_slug = request.args.get("species", "").strip(); status = request.args.get("status", "available").strip(); size = request.args.get("size", "").strip(); sort = request.args.get("sort", "new")
    if keyword:
        like = f"%{keyword}%"; query = query.filter(or_(Pet.name.ilike(like), Pet.temperament.ilike(like), Pet.location.ilike(like)))
    if species_slug: query = query.join(Species).filter(Species.slug == species_slug)
    if status: query = query.filter(Pet.status == status)
    if size: query = query.filter(Pet.size == size)
    query = query.order_by(Pet.view_count.desc() if sort == "popular" else Pet.created_at.desc())
    pagination = query.paginate(page=max(1, request.args.get("page", 1, type=int)), per_page=9, error_out=False)
    return render_template("pets/index.html", pets=pagination.items, pagination=pagination, species=Species.query.all(), keyword=keyword, active_species=species_slug, status=status, size=size, sort=sort)


@pets_bp.route("/<int:pet_id>")
def detail(pet_id):
    pet = db.get_or_404(Pet, pet_id); pet.view_count += 1; db.session.commit()
    favorite = application = None
    if current_user.is_authenticated:
        favorite = Favorite.query.filter_by(user_id=current_user.id, pet_id=pet.id).first()
        application = AdoptionApplication.query.filter_by(user_id=current_user.id, pet_id=pet.id).first()
    related = Pet.query.filter(Pet.species_id == pet.species_id, Pet.id != pet.id, Pet.status == "available").limit(3).all()
    return render_template("pets/detail.html", pet=pet, is_favorite=bool(favorite), application=application, related=related)


def _prepare_form(form):
    form.species_id.choices = [(item.id, item.name) for item in Species.query.order_by(Species.id)]
    images = ["pet-dog-sunny.png","pet-cat-mochi.png","pet-dog-coffee.png","pet-cat-sesame.png","pet-dog-cloud.png","pet-cat-orange.png"]
    form.cover_image.choices = [(name, name.replace("pet-", "").replace(".png", "")) for name in images]


@pets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if not current_user.is_shelter: abort(403)
    form = PetForm(); _prepare_form(form)
    if form.validate_on_submit():
        pet = Pet(code=f"PAW-{datetime.now().strftime('%y%m%d%H%M%S')}", name=form.name.data.strip(), species_id=form.species_id.data, sex=form.sex.data, age_months=form.age_months.data, size=form.size.data, color=form.color.data.strip(), temperament=form.temperament.data.strip(), location=form.location.data.strip(), cover_image=form.cover_image.data, description=form.description.data.strip(), rescue_story=form.rescue_story.data.strip(), vaccinated=form.vaccinated.data, neutered=form.neutered.data, shelter=current_user)
        db.session.add(pet); db.session.commit(); flash("宠物档案已创建", "success"); return redirect(url_for("pets.detail", pet_id=pet.id))
    return render_template("pets/form.html", form=form, pet=None)


@pets_bp.route("/<int:pet_id>/edit", methods=["GET", "POST"])
@login_required
def edit(pet_id):
    pet = db.get_or_404(Pet, pet_id)
    if pet.shelter_id != current_user.id and not current_user.is_admin: abort(403)
    form = PetForm(obj=pet); _prepare_form(form)
    if form.validate_on_submit():
        for field in ["name","species_id","sex","age_months","size","color","temperament","location","cover_image","description","rescue_story","vaccinated","neutered"]: setattr(pet, field, getattr(form, field).data)
        db.session.commit(); flash("宠物档案已更新", "success"); return redirect(url_for("pets.detail", pet_id=pet.id))
    return render_template("pets/form.html", form=form, pet=pet)


@pets_bp.route("/<int:pet_id>/manage")
@login_required
def manage(pet_id):
    pet = db.get_or_404(Pet, pet_id)
    if pet.shelter_id != current_user.id and not current_user.is_admin: abort(403)
    return render_template("pets/manage.html", pet=pet)
