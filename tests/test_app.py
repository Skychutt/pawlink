from datetime import datetime, timedelta

from app.extensions import db
from app.models import AdoptionApplication, AiConversation, AiMessage, Comment, Favorite, Pet, User, VisitAppointment, VolunteerSignup
from app.services.deepseek import DeepSeekService
from tests.conftest import login


def test_public_pages_render(client):
    for path in ["/","/pets/","/pets/1","/volunteer","/about"]:
        response=client.get(path); assert response.status_code==200
    assert "暖爪" in client.get("/").get_data(as_text=True)


def test_register_login_and_profile(client,app):
    response=client.post("/auth/register",data={"username":"newuser","display_name":"新用户","email":"new@example.com","phone":"13812345678","city":"杭州","password":"123456","confirm_password":"123456","agree":"y"},follow_redirects=True)
    assert response.status_code==200
    with app.app_context(): assert User.query.filter_by(username="newuser").first()
    assert client.get("/dashboard/profile").status_code==200


def test_favorite_comment_and_login_guard(client,app):
    assert client.post("/api/pets/1/favorite",json={}).status_code==401
    login(client)
    assert client.post("/api/pets/1/favorite",json={}).json["active"] is True
    assert client.post("/api/pets/1/comments",json={"content":"它平时运动量大吗？"}).status_code==200
    with app.app_context(): assert Favorite.query.count()==1 and Comment.query.count()==1


def test_application_and_visit_workflow(client,app):
    login(client)
    response=client.post("/api/pets/1/applications",json={"reason":"我已经与家人充分讨论并准备长期负责照顾它。","home_type":"自有住宅","contact":"13800000003","experience":"学习中","has_pets":False})
    assert response.status_code==200
    response=client.post("/api/pets/1/appointments",json={"scheduled_at":(datetime.now()+timedelta(days=2)).isoformat(timespec="minutes"),"note":"两人到访"})
    assert response.status_code==200
    with app.app_context(): assert AdoptionApplication.query.count()==1 and VisitAppointment.query.count()==1


def test_shelter_reviews_application(client,app):
    login(client); client.post("/api/pets/1/applications",json={"reason":"我已经做好长期稳定照顾它的充分准备和家庭安排。","home_type":"自有住宅","contact":"13800000003","experience":"无"})
    client.post("/auth/logout"); login(client,"shelter")
    assert client.get("/shelter/").status_code==200 and client.get("/pets/1/manage").status_code==200
    response=client.post("/api/applications/1/status",json={"status":"approved","note":"通过初审"}); assert response.status_code==200
    with app.app_context(): assert db.session.get(Pet,1).status=="pending"


def test_admin_pages_and_user_toggle(client,app):
    login(client,"admin","admin123")
    for path in ["/admin/","/admin/pets","/admin/users"]: assert client.get(path).status_code==200
    response=client.post("/api/admin/users/3/toggle",json={}); assert response.status_code==200 and response.json["active"] is False


def test_volunteer_signup(client,app):
    login(client); response=client.post("/api/volunteer/1/signup",json={}); assert response.status_code==200 and response.json["active"] is True
    with app.app_context(): assert VolunteerSignup.query.count()==1


def test_ai_requires_configuration(client):
    login(client); assert client.get("/api/ai/history").json["configured"] is False
    response=client.post("/api/ai/chat",json={"message":"推荐一只性格安静的动物"}); assert response.status_code==503


def test_ai_conversation_history_and_clear(client,app,monkeypatch):
    app.config["DEEPSEEK_API_KEY"]="test-key"; monkeypatch.setattr(DeepSeekService,"chat",lambda self,messages,event_context:"可以先认识小满。")
    login(client); response=client.post("/api/ai/chat",json={"message":"推荐一只狗狗"}); assert response.status_code==200
    assert [m["role"] for m in client.get("/api/ai/history").json["messages"]]==["user","assistant"]
    assert client.post("/api/ai/clear",json={}).status_code==200
    with app.app_context(): assert AiConversation.query.count()==0 and AiMessage.query.count()==0


def test_security_headers(client):
    response=client.get("/"); assert response.headers["X-Content-Type-Options"]=="nosniff"; assert "default-src 'self'" in response.headers["Content-Security-Policy"]
