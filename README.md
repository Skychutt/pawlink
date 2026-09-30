# 暖爪 PawLink｜动物救助与科学领养平台

基于 **Python Flask + SQLite + jQuery** 的完整课程设计项目。平台围绕“透明救助、负责领养、持续回访”构建，包含领养人、救助站工作人员和平台管理员三类角色，并集成 DeepSeek 多轮 AI 养宠助手。

## 功能亮点

- 15 张关系数据表：用户、物种、宠物档案、收藏、领养申请、探访预约、健康记录、生活动态、留言、通知、公告、志愿活动、志愿报名，以及 AI 对话和消息。
- 完整领养闭环：浏览档案 → 收藏 → 提交申请 → 初审/面谈 → 预约见面 → 原则通过 → 完成领养。
- 透明宠物档案：基础身份、性格标签、救助故事、健康记录、免疫/绝育状态、近期动态和救助机构。
- 救助站工作台：新建/编辑档案、查看申请、填写审核备注、推进审核状态、查看探访预约。
- 平台管理台：用户、档案、申请、成功领养统计；物种分布图表；用户账号启停。
- 志愿活动：活动浏览、容量限制、AJAX 报名/取消和个人中心记录。
- 暖爪 AI：根据当前可领养动物档案进行推荐，解答领养准备与基础护理问题，保存多轮聊天。
- 安全设计：密码哈希、登录会话、CSRF、权限校验、安全响应头、API 限流和密钥后端隔离。
- 响应式设计：桌面、平板和手机布局，使用本地 jQuery 与 Chart.js。
- 8 张原创 AI 图片：首页主视觉、六份宠物档案照和志愿行动素材。

## 演示账号

| 身份 | 用户名 | 密码 | 演示内容 |
|---|---|---|---|
| 平台管理员 | `admin` | `admin123` | 运营统计、全部档案、用户管理 |
| 救助站工作人员 | `shelter` | `123456` | 建档、申请审核、预约和健康记录 |
| 普通领养人 | `xiaoyu` | `123456` | 收藏、申请、探访、志愿活动与 AI |

登录页可以点击演示账号自动填入。

## 快速运行

### PyCharm

1. 打开 `项目根目录`。
2. 项目解释器选择 `flask2\.venv\Scripts\python.exe`。
3. 选择运行配置 `PawLink 暖爪`，点击绿色运行按钮。
4. 浏览器打开 <http://127.0.0.1:5001>。

### 双击或命令行

可双击 `start.bat`，也可运行：

```powershell
.\.venv\Scripts\python.exe run.py
```

本项目使用 `5001` 端口，可以与 `flask1` 的 `5000` 端口同时运行。

## 首次重新安装

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app run.py init-db
```

`init-db` 会重建演示数据库，请勿在已保存正式数据时执行。

## 数据库与 MySQL

默认数据库为 `instance/pawlink.db`，使用 SQLite，不需要账号密码。课程要求 MySQL 时，在 `.env` 中设置：

```text
DATABASE_URL=mysql+pymysql://用户名:密码@127.0.0.1:3306/pawlink?charset=utf8mb4
```

并安装 `PyMySQL`。详细关系设计见 `docs/database-design.md`。

## DeepSeek AI 配置

复制 `.env.example` 为 `.env`，只在本机填写新生成的密钥：

```text
DEEPSEEK_API_KEY=你的新密钥
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-v4-flash
```

真实密钥不得写入代码、截图或聊天记录。`.env` 已被 `.gitignore` 排除。

## 自动化测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp instance\pytest-temp
```

测试覆盖公开页面、注册登录、收藏留言、领养申请、预约、救助站审核、管理员权限、志愿报名、AI 对话和安全响应头。

## 答辩演示建议

1. 游客浏览首页、筛选宠物并打开包含健康记录和救助故事的档案。
2. 用 `xiaoyu` 收藏宠物、提交申请、预约探访并参加志愿活动。
3. 用 `shelter` 在工作台查看材料并把申请推进到面谈或通过。
4. 用 `admin` 展示运营统计、图表、全部档案和用户管理。
5. 打开暖爪 AI，演示根据数据库档案进行多轮推荐。

## 技术栈

Python 3.11+、Flask 3、Blueprint、Jinja2、Flask-SQLAlchemy、Flask-Login、Flask-WTF、SQLite、HTML5、CSS3、jQuery 3.7.1、Chart.js、pytest。
