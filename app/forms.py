from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp


class LoginForm(FlaskForm):
    account = StringField("用户名或邮箱", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("密码", validators=[DataRequired()])
    remember = BooleanField("记住我", default=True)
    submit = SubmitField("登录")


class RegisterForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(3, 30), Regexp(r"^[A-Za-z0-9_]+$")])
    display_name = StringField("昵称", validators=[DataRequired(), Length(2, 40)])
    email = StringField("邮箱", validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField("联系电话", validators=[DataRequired(), Length(6, 30)])
    city = StringField("所在城市", validators=[DataRequired(), Length(2, 50)])
    password = PasswordField("密码", validators=[DataRequired(), Length(6, 64)])
    confirm_password = PasswordField("确认密码", validators=[DataRequired(), EqualTo("password")])
    agree = BooleanField("我已阅读并同意领养公约", validators=[DataRequired()])
    submit = SubmitField("创建账号")


class ProfileForm(FlaskForm):
    display_name = StringField("昵称", validators=[DataRequired(), Length(2, 40)])
    phone = StringField("联系电话", validators=[DataRequired(), Length(6, 30)])
    city = StringField("所在城市", validators=[DataRequired(), Length(2, 50)])
    bio = TextAreaField("个人介绍", validators=[Optional(), Length(max=240)])
    avatar_color = SelectField("头像颜色", choices=[("#c96f4a","暖橘"),("#52796f","鼠尾草绿"),("#355070","深海蓝"),("#b56576","莓果红")])
    submit = SubmitField("保存资料")


class PetForm(FlaskForm):
    name = StringField("名字", validators=[DataRequired(), Length(1, 50)])
    species_id = SelectField("种类", coerce=int, validators=[DataRequired()])
    sex = SelectField("性别", choices=[("公","公"),("母","母")])
    age_months = IntegerField("月龄", validators=[DataRequired(), NumberRange(1, 300)])
    size = SelectField("体型", choices=[("小型","小型"),("中型","中型"),("大型","大型")])
    color = StringField("毛色", validators=[Optional(), Length(max=50)])
    temperament = StringField("性格标签", validators=[DataRequired(), Length(2, 120)])
    location = StringField("所在地点", validators=[DataRequired(), Length(2, 100)])
    cover_image = SelectField("档案封面")
    description = TextAreaField("性格与习惯", validators=[DataRequired(), Length(20, 2000)])
    rescue_story = TextAreaField("救助故事", validators=[DataRequired(), Length(20, 2000)])
    vaccinated = BooleanField("已完成基础免疫")
    neutered = BooleanField("已绝育")
    submit = SubmitField("保存宠物档案")
