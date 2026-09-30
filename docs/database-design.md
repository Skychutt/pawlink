# 暖爪 PawLink 数据库设计

## 核心关系

- `user` 1:N `pet`：救助站工作人员维护宠物档案。
- `user` N:M `pet`：通过 `favorite` 建立收藏关系。
- `user` N:M `pet`：通过 `adoption_application` 保存领养申请及审核状态，每人每只动物限一份。
- `user` N:M `pet`：通过 `visit_appointment` 保存线下探访预约。
- `pet` 1:N `health_record`：公开体检、免疫、绝育和复诊记录。
- `pet` 1:N `pet_update`：救助人在档案中发布生活动态。
- `pet` 1:N `comment`：登录用户向救助人提问。
- `volunteer_activity` N:M `user`：通过 `volunteer_signup` 保存志愿报名。
- `user` 1:N `notification`：保存申请、预约与系统通知。
- `user` 1:N `ai_conversation` 1:N `ai_message`：保存个人多轮 AI 对话。

## 状态机

宠物：`available 等待领养` → `pending 审核中` → `adopted 已回家`；治疗阶段使用 `recovery 康复中`。

申请：`submitted 已提交` → `interview 进入面谈` → `approved 原则通过` → `completed 完成领养`；不匹配时进入 `rejected`。

## 约束与安全

- 用户名、邮箱和宠物档案编号唯一。
- 收藏与领养申请使用联合唯一约束，避免重复。
- 密码只保存哈希；DeepSeek 密钥仅从本机环境变量读取。
- 救助站只能管理本机构档案，管理员具备全局权限。
