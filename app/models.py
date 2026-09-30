from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


class User(UserMixin, TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(30), default="")
    city = db.Column(db.String(50), default="杭州")
    bio = db.Column(db.String(240), default="")
    organization = db.Column(db.String(100), default="")
    avatar_color = db.Column(db.String(20), default="#c96f4a")
    role = db.Column(db.String(20), default="adopter", nullable=False)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)

    pets = db.relationship("Pet", back_populates="shelter", cascade="all, delete-orphan")
    applications = db.relationship("AdoptionApplication", back_populates="user", cascade="all, delete-orphan")
    appointments = db.relationship("VisitAppointment", back_populates="user", cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    volunteer_signups = db.relationship("VolunteerSignup", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = db.relationship("AiConversation", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    @property
    def is_admin(self): return self.role == "admin"
    @property
    def is_shelter(self): return self.role in {"shelter", "admin"}
    @property
    def is_active(self): return self.is_active_account


class Species(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(120), default="")
    pets = db.relationship("Pet", back_populates="species")


class Pet(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    sex = db.Column(db.String(10), nullable=False)
    age_months = db.Column(db.Integer, nullable=False)
    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), default="")
    temperament = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rescue_story = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(160), nullable=False, default="pet-default.png")
    status = db.Column(db.String(20), default="available", nullable=False, index=True)
    vaccinated = db.Column(db.Boolean, default=False, nullable=False)
    neutered = db.Column(db.Boolean, default=False, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"), nullable=False)
    shelter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    species = db.relationship("Species", back_populates="pets")
    shelter = db.relationship("User", back_populates="pets")
    favorites = db.relationship("Favorite", back_populates="pet", cascade="all, delete-orphan")
    applications = db.relationship("AdoptionApplication", back_populates="pet", cascade="all, delete-orphan")
    appointments = db.relationship("VisitAppointment", back_populates="pet", cascade="all, delete-orphan")
    health_records = db.relationship("HealthRecord", back_populates="pet", cascade="all, delete-orphan", order_by="HealthRecord.record_date.desc()")
    updates = db.relationship("PetUpdate", back_populates="pet", cascade="all, delete-orphan", order_by="PetUpdate.created_at.desc()")
    comments = db.relationship("Comment", back_populates="pet", cascade="all, delete-orphan", order_by="Comment.created_at.desc()")

    @property
    def age_text(self):
        if self.age_months < 12: return f"{self.age_months}个月"
        years, months = divmod(self.age_months, 12)
        return f"{years}岁" + (f"{months}个月" if months else "")
    @property
    def status_text(self):
        return {"available":"等待领养", "pending":"审核中", "adopted":"已回家", "recovery":"康复中"}.get(self.status, self.status)


class Favorite(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    user = db.relationship("User", back_populates="favorites")
    pet = db.relationship("Pet", back_populates="favorites")
    __table_args__ = (db.UniqueConstraint("user_id", "pet_id", name="uq_favorite_user_pet"),)


class AdoptionApplication(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(800), nullable=False)
    home_type = db.Column(db.String(40), nullable=False)
    experience = db.Column(db.String(500), default="")
    has_pets = db.Column(db.Boolean, default=False, nullable=False)
    contact = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(20), default="submitted", nullable=False, index=True)
    review_note = db.Column(db.String(400), default="")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    user = db.relationship("User", back_populates="applications")
    pet = db.relationship("Pet", back_populates="applications")
    __table_args__ = (db.UniqueConstraint("user_id", "pet_id", name="uq_application_user_pet"),)


class VisitAppointment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.String(300), default="")
    status = db.Column(db.String(20), default="pending", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    user = db.relationship("User", back_populates="appointments")
    pet = db.relationship("Pet", back_populates="appointments")


class HealthRecord(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.Date, nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    veterinarian = db.Column(db.String(80), default="")
    next_due = db.Column(db.Date, nullable=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    pet = db.relationship("Pet", back_populates="health_records")


class PetUpdate(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(600), nullable=False)
    image = db.Column(db.String(160), default="")
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet = db.relationship("Pet", back_populates="updates")
    author = db.relationship("User")


class Comment(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey("pet.id"), nullable=False)
    user = db.relationship("User", back_populates="comments")
    pet = db.relationship("Pet", back_populates="comments")


class Notification(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(260), nullable=False)
    link = db.Column(db.String(200), default="")
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="notifications")


class Announcement(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(260), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class VolunteerActivity(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    starts_at = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, default=20, nullable=False)
    cover_image = db.Column(db.String(160), nullable=False)
    signups = db.relationship("VolunteerSignup", back_populates="activity", cascade="all, delete-orphan")


class VolunteerSignup(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default="joined", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("volunteer_activity.id"), nullable=False)
    user = db.relationship("User", back_populates="volunteer_signups")
    activity = db.relationship("VolunteerActivity", back_populates="signups")
    __table_args__ = (db.UniqueConstraint("user_id", "activity_id", name="uq_volunteer_user_activity"),)


class AiConversation(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="暖爪 AI 对话", nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    user = db.relationship("User", back_populates="ai_conversations")
    messages = db.relationship("AiMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AiMessage.created_at.asc()")


class AiMessage(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey("ai_conversation.id"), nullable=False, index=True)
    conversation = db.relationship("AiConversation", back_populates="messages")
