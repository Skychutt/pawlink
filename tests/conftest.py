from datetime import datetime, timedelta

import pytest

from app import create_app
from app.extensions import db
from app.models import Pet, Species, User, VolunteerActivity


@pytest.fixture()
def app(tmp_path):
    app=create_app({"TESTING":True,"WTF_CSRF_ENABLED":False,"SQLALCHEMY_DATABASE_URI":f"sqlite:///{(tmp_path/'test.db').as_posix()}","SECRET_KEY":"test","DEEPSEEK_API_KEY":""})
    with app.app_context():
        db.create_all(); dog=Species(name="狗狗",slug="dogs",icon="犬")
        admin=User(username="admin",email="admin@test.local",display_name="管理员",phone="13800000001",role="admin"); admin.set_password("admin123")
        shelter=User(username="shelter",email="shelter@test.local",display_name="救助人",phone="13800000002",role="shelter",organization="测试救助站"); shelter.set_password("123456")
        adopter=User(username="adopter",email="adopter@test.local",display_name="领养人",phone="13800000003"); adopter.set_password("123456")
        db.session.add_all([dog,admin,shelter,adopter]); db.session.flush()
        pet=Pet(code="TEST-001",name="小满",species=dog,shelter=shelter,sex="母",age_months=18,size="中型",color="浅黄",temperament="温柔 · 亲人",description="这是一份足够完整的测试性格描述，用于验证宠物详情页面与领养业务流程。",rescue_story="这是一个完整的测试救助故事，用于验证公开档案中的救助信息能够正确展示。",location="测试救助站",cover_image="pet-dog-sunny.png",status="available",vaccinated=True,neutered=True)
        activity=VolunteerActivity(title="测试志愿活动",description="测试活动描述",location="测试地点",starts_at=datetime.now()+timedelta(days=5),capacity=10,cover_image="volunteer-walk.png")
        db.session.add_all([pet,activity]); db.session.commit()
    yield app


@pytest.fixture()
def client(app): return app.test_client()


def login(client,account="adopter",password="123456"):
    return client.post("/auth/login",data={"account":account,"password":password},follow_redirects=True)
