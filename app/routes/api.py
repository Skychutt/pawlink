import time
from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session, url_for
from flask_login import current_user

from ..extensions import db
from ..models import (AdoptionApplication, AiConversation, AiMessage, Comment, Favorite, Notification, Pet, User, VisitAppointment, VolunteerActivity, VolunteerSignup)
from ..services.deepseek import DeepSeekError, DeepSeekService

api_bp = Blueprint("api", __name__)


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated: return jsonify(ok=False, message="请先登录", redirect=url_for("auth.login", next=request.referrer or "/")), 401
        return view(*args, **kwargs)
    return wrapped


def api_shelter_required(view):
    @wraps(view)
    @api_login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_shelter: return jsonify(ok=False, message="没有救助站管理权限"), 403
        return view(*args, **kwargs)
    return wrapped


def api_admin_required(view):
    @wraps(view)
    @api_login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin: return jsonify(ok=False, message="没有管理员权限"), 403
        return view(*args, **kwargs)
    return wrapped


@api_bp.post("/pets/<int:pet_id>/favorite")
@api_login_required
def favorite(pet_id):
    pet=db.get_or_404(Pet,pet_id); item=Favorite.query.filter_by(user_id=current_user.id,pet_id=pet.id).first()
    if item: db.session.delete(item); active=False; message="已取消收藏"
    else: db.session.add(Favorite(user=current_user,pet=pet)); active=True; message="已加入心愿单"
    db.session.commit(); return jsonify(ok=True,active=active,message=message)


@api_bp.post("/pets/<int:pet_id>/applications")
@api_login_required
def apply(pet_id):
    pet=db.get_or_404(Pet,pet_id)
    if pet.status!="available": return jsonify(ok=False,message="该宠物当前不可申请领养"),400
    if AdoptionApplication.query.filter_by(user_id=current_user.id,pet_id=pet.id).first(): return jsonify(ok=False,message="你已经提交过领养申请"),409
    data=request.get_json(silent=True) or {}; reason=str(data.get("reason","")).strip(); home_type=str(data.get("home_type","")).strip(); contact=str(data.get("contact","")).strip(); experience=str(data.get("experience","")).strip()
    if len(reason)<20 or not home_type or len(contact)<6: return jsonify(ok=False,message="请完整填写居住条件、联系方式和不少于20字的领养计划"),400
    application=AdoptionApplication(reason=reason,home_type=home_type,contact=contact,experience=experience,has_pets=bool(data.get("has_pets")),user=current_user,pet=pet)
    db.session.add(application); db.session.add(Notification(user=pet.shelter,title="收到新的领养申请",content=f"{current_user.display_name} 申请领养 {pet.name}",link=url_for("pets.manage",pet_id=pet.id))); db.session.commit()
    return jsonify(ok=True,message="申请已提交，救助站会尽快与你联系",status=application.status)


@api_bp.post("/pets/<int:pet_id>/appointments")
@api_login_required
def appointment(pet_id):
    pet=db.get_or_404(Pet,pet_id); data=request.get_json(silent=True) or {}
    try: scheduled=datetime.fromisoformat(str(data.get("scheduled_at","")))
    except ValueError: return jsonify(ok=False,message="请选择有效的探访日期和时间"),400
    if scheduled<=datetime.now(): return jsonify(ok=False,message="探访时间必须晚于现在"),400
    item=VisitAppointment(scheduled_at=scheduled,note=str(data.get("note","")).strip()[:300],user=current_user,pet=pet); db.session.add(item); db.session.commit()
    return jsonify(ok=True,message="探访预约已提交",time=scheduled.strftime("%m月%d日 %H:%M"))


@api_bp.post("/pets/<int:pet_id>/comments")
@api_login_required
def comment(pet_id):
    pet=db.get_or_404(Pet,pet_id); content=str((request.get_json(silent=True) or {}).get("content","")).strip()
    if not 2<=len(content)<=500: return jsonify(ok=False,message="留言长度需要在2—500字之间"),400
    item=Comment(content=content,user=current_user,pet=pet); db.session.add(item); db.session.commit()
    return jsonify(ok=True,message="留言发布成功",comment={"content":content,"author":current_user.display_name,"initial":current_user.display_name[0],"avatar_color":current_user.avatar_color})


@api_bp.post("/applications/<int:application_id>/status")
@api_shelter_required
def application_status(application_id):
    item=db.get_or_404(AdoptionApplication,application_id)
    if item.pet.shelter_id!=current_user.id and not current_user.is_admin: return jsonify(ok=False,message="无权审核此申请"),403
    data=request.get_json(silent=True) or {}; status=data.get("status")
    if status not in {"interview","approved","rejected","completed"}: return jsonify(ok=False,message="状态值不正确"),400
    item.status=status; item.review_note=str(data.get("note","")).strip()[:400]
    if status=="approved": item.pet.status="pending"
    elif status=="completed": item.pet.status="adopted"
    db.session.add(Notification(user=item.user,title="领养申请进度更新",content=f"你对 {item.pet.name} 的申请状态更新为：{status}",link=url_for("dashboard.index"))); db.session.commit()
    return jsonify(ok=True,message="申请状态已更新",status=status,pet_status=item.pet.status)


@api_bp.post("/volunteer/<int:activity_id>/signup")
@api_login_required
def volunteer_signup(activity_id):
    activity=db.get_or_404(VolunteerActivity,activity_id); item=VolunteerSignup.query.filter_by(user_id=current_user.id,activity_id=activity.id).first()
    if item: db.session.delete(item); active=False; message="已取消志愿报名"
    elif len(activity.signups)>=activity.capacity: return jsonify(ok=False,message="本场志愿活动名额已满"),400
    else: db.session.add(VolunteerSignup(user=current_user,activity=activity)); active=True; message="志愿活动报名成功"
    db.session.commit(); return jsonify(ok=True,active=active,message=message,count=len(activity.signups))


@api_bp.post("/notifications/read")
@api_login_required
def read_notifications():
    Notification.query.filter_by(user_id=current_user.id,is_read=False).update({"is_read":True}); db.session.commit(); return jsonify(ok=True,message="通知已全部标为已读")


@api_bp.post("/admin/users/<int:user_id>/toggle")
@api_admin_required
def toggle_user(user_id):
    user=db.get_or_404(User,user_id)
    if user.id==current_user.id: return jsonify(ok=False,message="不能停用自己的管理员账号"),400
    user.is_active_account=not user.is_active_account; db.session.commit(); return jsonify(ok=True,active=user.is_active_account,message="账号状态已更新")


def _ai_service():
    return DeepSeekService(current_app.config["DEEPSEEK_API_KEY"],current_app.config["DEEPSEEK_API_URL"],current_app.config["DEEPSEEK_MODEL"],current_app.config["DEEPSEEK_TIMEOUT"])


def _conversation(): return AiConversation.query.filter_by(user_id=current_user.id).order_by(AiConversation.updated_at.desc()).first()


@api_bp.get("/ai/history")
@api_login_required
def ai_history():
    service=_ai_service(); conversation=_conversation(); messages=[] if not conversation else [{"role":m.role,"content":m.content,"time":m.created_at.strftime("%H:%M")} for m in conversation.messages[-40:]]
    return jsonify(ok=True,configured=service.is_configured,model=current_app.config["DEEPSEEK_MODEL"],messages=messages)


@api_bp.post("/ai/chat")
@api_login_required
def ai_chat():
    service=_ai_service()
    if not service.is_configured: return jsonify(ok=False,message="AI服务尚未配置，请先设置DeepSeek API Key"),503
    content=str((request.get_json(silent=True) or {}).get("message","")).strip()
    if not 1<=len(content)<=1000: return jsonify(ok=False,message="问题长度需要在1—1000字之间"),400
    stamps=[x for x in session.get("ai_request_times",[]) if time.time()-float(x)<60]
    if len(stamps)>=8: return jsonify(ok=False,message="提问太快，请一分钟后再试"),429
    stamps.append(time.time()); session["ai_request_times"]=stamps
    conversation=_conversation(); history=[] if not conversation else [{"role":m.role,"content":m.content} for m in conversation.messages[-12:]]; history.append({"role":"user","content":content})
    context="\n".join(f"- {p.name}：{p.species.name}，{p.age_text}，{p.temperament}，位于{p.location}" for p in Pet.query.filter_by(status="available").limit(8))
    try: answer=service.chat(history,context)
    except DeepSeekError as error: return jsonify(ok=False,message=str(error)),502
    if conversation is None: conversation=AiConversation(user=current_user,title=content[:40]); db.session.add(conversation); db.session.flush()
    conversation.updated_at=datetime.now(); db.session.add_all([AiMessage(conversation=conversation,role="user",content=content),AiMessage(conversation=conversation,role="assistant",content=answer)]); db.session.commit()
    return jsonify(ok=True,answer=answer,time=datetime.now().strftime("%H:%M"),model=current_app.config["DEEPSEEK_MODEL"])


@api_bp.post("/ai/clear")
@api_login_required
def ai_clear():
    item=_conversation()
    if item: db.session.delete(item); db.session.commit()
    return jsonify(ok=True,message="对话记录已清空")
