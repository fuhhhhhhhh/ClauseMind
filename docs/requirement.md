# ClauseMind 需求文档

## 项目背景
ClauseMind 是一个基于 React + FastAPI + MinerU + 多 Agent 的合同智能审查系统。面向个人、小微企业和普通办公场景中的合同阅读与风险初筛需求。

系统整体流程：
用户上传合同 → MinerU 解析 → 文档标准化 → 多 Agent 审查 → 报告生成 → 前端展示

## 功能需求

### 用户与鉴权
- 用户注册（用户名 + 密码 + 可选邮箱）
- 用户登录（返回 JWT）
- JWT 鉴权（Bearer Token）
- 获取当前用户信息

### 合同管理
- 上传合同文件（PDF/DOCX/TXT/PNG/JPG/JPEG，最大 50MB）
- UUID 文件名持久化
- 合同列表/详情/删除（用户隔离）
- 管理员查看所有合同

### MinerU 解析
- 调用 MinerU CLI 解析
- 收集 Markdown/content_list.json/middle.json/layout.pdf
- 状态跟踪（WAITING/RUNNING/SUCCESS/FAILED）
- 合同状态流转（UPLOADED→PARSING→PARSED/FAILED）

### 文档标准化
- 标题、主体（甲方/乙方等）提取
- 条款规则识别（第一条、1.、1.1、（一）等）
- 表格提取
- 结构化 JSON 持久化

### 多 Agent 审查（6 Agent 顺序执行）
1. ContractProfileAgent — 合同画像
2. ClauseExtractionAgent — 条款抽取
3. RiskDetectionAgent — 风险识别
4. SuggestionAgent — 修改建议
5. ConsistencyCheckAgent — 一致性校验
6. ReportGenerationAgent — 报告生成

每个 Agent 记录输入/输出/状态/耗时/错误。

### 审查结果
- 条款/风险/建议查询
- 审查报告（Markdown + 免责声明）
- 报告导出（Markdown 下载）

### 管理员后台
- 用户/合同/审查任务/Agent 日志管理
- 系统统计（用户数/合同数/风险统计）

## 非功能需求
- 前后端分离（React + FastAPI）
- SQLite（可切换 MySQL）
- Alembic 迁移管理
- OpenAI-compatible LLM
- 所有接口鉴权，用户数据隔离
- 不暴露服务器内部路径
- 报告必须包含免责声明

## 角色
- USER：管理自己的合同、启动审查、查看结果
- admin：查看所有用户/合同/任务/日志/统计

## 业务流程
1. 注册/登录
2. 上传合同
3. MinerU 解析
4. 文档标准化
5. 启动审查工作流
6. 查看风险/建议/报告
7. 导出报告
