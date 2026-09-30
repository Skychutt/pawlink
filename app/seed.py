from datetime import date, datetime, timedelta

import click

from .extensions import db
from .models import (AdoptionApplication, Announcement, Comment, Favorite, HealthRecord, Notification, Pet, PetUpdate, Species, User, VisitAppointment, VolunteerActivity, VolunteerSignup)


def _future(days, hour=10):
    value=datetime.now()+timedelta(days=days); return value.replace(hour=hour,minute=0,second=0,microsecond=0)


def seed_database():
    db.drop_all(); db.create_all()
    species=[Species(name="狗狗",slug="dogs",icon="犬",description="忠诚、热情，适合愿意稳定陪伴的家庭"),Species(name="猫咪",slug="cats",icon="猫",description="安静独立，也需要长期负责的照顾"),Species(name="兔子",slug="rabbits",icon="兔",description="温柔敏感，需要科学饮食与合适空间"),Species(name="其他",slug="others",icon="伴",description="每一种生命都值得被认真了解")]
    db.session.add_all(species)
    admin=User(username="admin",email="admin@pawlink.test",display_name="平台管理员",phone="13800000001",city="杭州",role="admin",organization="暖爪平台运营中心",avatar_color="#355070",bio="负责平台审核、数据运营与合作机构管理。")
    shelter=User(username="shelter",email="shelter@pawlink.test",display_name="林岚",phone="13800000002",city="杭州",role="shelter",organization="晨光动物救助站",avatar_color="#52796f",bio="从事小动物救助与领养回访，希望每一次相遇都建立在理解和责任上。")
    adopter=User(username="xiaoyu",email="xiaoyu@pawlink.test",display_name="小雨",phone="13800000003",city="杭州",role="adopter",avatar_color="#c96f4a",bio="正在认真学习科学养宠，希望遇见适合彼此的家人。")
    volunteer=User(username="anran",email="anran@pawlink.test",display_name="安然",phone="13800000004",city="杭州",role="adopter",avatar_color="#b56576",bio="周末救助志愿者，喜欢给待领养动物拍好看的照片。")
    for user,password in [(admin,"admin123"),(shelter,"123456"),(adopter,"123456"),(volunteer,"123456")]: user.set_password(password)
    db.session.add_all([admin,shelter,adopter,volunteer]); db.session.flush()
    data=[
        ("PAW-2401","晴天",species[0],"母",30,"中型","奶油色","亲人 · 稳定 · 会坐下", "pet-dog-sunny.png","available",True,True,"在城郊工地附近被发现，刚来时有些紧张。经过三个月寄养，晴天已经学会牵引随行和基础指令。","晴天喜欢慢慢认识新朋友，在熟悉的人身边会把头靠过来。每天需要两次散步，适合生活节奏稳定的家庭。"),
        ("PAW-2402","糯米",species[1],"母",18,"小型","银虎斑","安静 · 好奇 · 亲猫", "pet-cat-mochi.png","available",True,True,"由社区绝育项目转入，体检后进入家庭寄养。她很快适应室内生活，也愿意和温和的猫相处。","糯米白天喜欢窗边晒太阳，晚上会主动来找人玩逗猫棒。对突然的巨大声音比较敏感。"),
        ("PAW-2403","咖啡",species[0],"公",42,"中型","棕色","活泼 · 聪明 · 爱玩球", "pet-dog-coffee.png","available",True,True,"原主人因长期住院无法继续照顾，经协商后由救助站接收。过往生活稳定，社会化良好。","咖啡精力充沛，喜欢捡球和嗅闻游戏。希望新家庭每天能提供充足运动，不建议与小型啮齿动物同住。"),
        ("PAW-2404","芝麻",species[1],"公",14,"小型","黑白","机灵 · 亲人 · 爱观察", "pet-cat-sesame.png","available",True,True,"幼年时在停车场获救，完成治疗后一直生活在开放式猫房。","芝麻是猫房里的观察员，会在高处认真看每一个人。熟悉后非常粘人，适合有耐心的领养家庭。"),
        ("PAW-2405","云朵",species[0],"母",8,"中型","浅黄","胆小 · 温柔 · 学习中", "pet-dog-cloud.png","recovery",False,False,"雨天在高架桥下被志愿者发现，目前正在完成皮肤和营养康复。","云朵还在学习相信人类，暂不开放正式领养，可以先通过志愿陪伴与她建立关系。"),
        ("PAW-2406","橘子",species[1],"公",36,"小型","橘白","慢热 · 爱吃 · 适合独宠", "pet-cat-orange.png","pending",True,True,"社区居民共同照顾多年，因施工环境变化转入救助站。","橘子需要一点时间熟悉新环境，一旦放松就会发出很响的呼噜声。目前已有家庭进入面谈。"),
    ]
    pets=[]
    for code,name,kind,sex,age,size,color,temp,image,status,vac,neu,story,desc in data:
        pet=Pet(code=code,name=name,species=kind,sex=sex,age_months=age,size=size,color=color,temperament=temp,cover_image=image,status=status,vaccinated=vac,neutered=neu,rescue_story=story,description=desc,location="晨光动物救助站·杭州",featured=name in {"晴天","糯米","咖啡"},view_count={"晴天":628,"糯米":514,"咖啡":443}.get(name,180),shelter=shelter); pets.append(pet)
    db.session.add_all(pets); db.session.flush()
    for pet in pets[:4]:
        db.session.add_all([HealthRecord(pet=pet,record_date=date.today()-timedelta(days=20),record_type="健康体检",description="体温、心肺、口腔与基础血检无明显异常。",veterinarian="周医生"),HealthRecord(pet=pet,record_date=date.today()-timedelta(days=50),record_type="免疫记录",description="完成核心疫苗与体内外驱虫。",veterinarian="晨光合作动物医院",next_due=date.today()+timedelta(days=315))])
        db.session.add(PetUpdate(pet=pet,author=shelter,content=f"{pet.name} 本周状态稳定，已经完成新的环境适应练习，也拍下了一张很放松的照片。",image=pet.cover_image))
    application=AdoptionApplication(user=adopter,pet=pets[5],reason="我和家人已经认真讨论过长期养猫的责任，住房稳定且已封窗，希望给橘子一个安静的独宠家庭。",home_type="自有住宅·已封窗",experience="曾照顾家人猫咪两年",has_pets=False,contact="微信同手机号",status="interview",review_note="已完成电话沟通，等待线下见面")
    db.session.add_all([application,Favorite(user=adopter,pet=pets[0]),Favorite(user=adopter,pet=pets[1]),Comment(user=adopter,pet=pets[0],content="晴天平时可以和其他狗狗友好相处吗？周末想先预约见面。"),Comment(user=shelter,pet=pets[0],content="在正确介绍的情况下相处很好，我们会在见面时安排安全的社交测试。"),VisitAppointment(user=adopter,pet=pets[5],scheduled_at=_future(3,14),note="两位家庭成员一起到访",status="confirmed")])
    walk=VolunteerActivity(title="周末晨光遛犬小队",description="完成培训后，协助救助站犬只进行分组散步、嗅闻探索和基础社会化记录。",location="青山湖绿道东入口",starts_at=_future(7,8),capacity=18,cover_image="volunteer-walk.png")
    photo=VolunteerActivity(title="待领养动物影像日",description="为待领养动物拍摄档案照与短视频，帮助它们被更多合适的家庭看见。",location="晨光动物救助站",starts_at=_future(14,9),capacity=12,cover_image="hero-pawlink.png")
    db.session.add_all([walk,photo]); db.session.flush(); db.session.add(VolunteerSignup(user=volunteer,activity=walk))
    db.session.add_all([Announcement(title="领养不是领取，而是一份长期承诺",content="提交申请前，请先阅读领养流程并完成家庭成员沟通。平台不收取领养费用。"),Notification(user=adopter,title="见面预约已确认",content="你与橘子的见面安排已确认，请按时到达并携带身份证件。",link="/dashboard/")])
    db.session.commit()


def register_commands(app):
    @app.cli.command("init-db")
    def init_db_command(): seed_database(); click.echo("暖爪 PawLink 数据库与演示数据初始化完成。")
