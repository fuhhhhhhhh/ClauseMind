# CLAUDE.md / PROJECT_SPEC.md

# 基于 React + FastAPI + MinerU + 多 Agent 的合同智能审查系统

> 本文件用于指导 AI 编程助手实现项目。  
> 后续生成代码时，应严格围绕本文档中的系统边界、技术架构、模块划分、数据结构、接口设计和实现顺序进行。  
> 本项目采用 React 前端 + FastAPI 后端，不使用 Java / Spring Boot。  
> 本项目定位为课程结课设计项目，不追求法律专业级准确性，而是实现一个工程完整、结构清晰、具备 AI 服务能力的合同辅助审查系统。

---

## 0. 项目定位

### 0.1 项目名称

基于 MinerU 与多 Agent 协作的合同智能审查系统

英文名可用：

```text
MinerU Multi-Agent Contract Review System
```

### 0.2 项目目标

本系统面向个人、小微企业和普通办公场景中的合同阅读与风险初筛需求，提供合同上传、文档解析、合同结构化、条款抽取、风险识别、修改建议、报告生成等功能。

系统整体流程：

```text
用户上传合同文件
→ FastAPI 保存文件并创建合同记录
→ 调用 MinerU 解析 PDF / DOCX / 图片合同
→ 将 MinerU 输出的 Markdown / JSON 标准化为合同结构
→ 多 Agent 按步骤进行合同审查
→ 保存每个 Agent 的输入、输出和执行日志
→ 生成合同审查报告
→ React 前端展示风险项、修改建议和最终报告
```

### 0.3 系统边界

本系统是“合同辅助审查系统”，不是律师系统，也不是法律裁判系统。

系统可以做：

```text
1. 合同文件上传
2. MinerU 文档解析
3. Markdown / JSON 结果预览
4. 合同章节标准化
5. 合同基本信息提取
6. 关键条款抽取
7. 常见风险提示
8. 条款修改建议
9. 一致性校验
10. 审查报告生成
11. Agent 执行过程追踪
```

系统不做：

```text
1. 不给出最终法律结论
2. 不判断合同一定违法或无效
3. 不替代律师审查
4. 不承诺风险识别完全准确
5. 不接入真实法院、律所或政务系统
6. 不做在线签约
7. 不做支付系统
```

所有报告必须包含免责声明：

```text
本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。
```

---

## 1. 技术栈

### 1.1 总体技术方案

本项目采用：

```text
React 前端
    ↓ HTTP / REST API
FastAPI 后端
    ├── 用户与权限管理
    ├── 合同文件管理
    ├── MinerU 文档解析
    ├── 文档标准化
    ├── 多 Agent 审查
    ├── 审查报告生成
    └── 管理员后台 API
    ↓
MySQL / SQLite
    ↓
本地文件存储
```

不再拆分 Java 业务后端和 Python AI 服务，所有后端能力统一由 FastAPI 实现。

推荐原因：

```text
1. 单人开发更轻量
2. 后端和 AI 服务都在 Python 生态中，方便集成 MinerU 和 LLM
3. 不需要处理 Java 后端调用 Python 服务的额外复杂度
4. FastAPI 天然适合文件上传、异步任务、AI 服务封装
5. React 前端展示效果好，适合做 Dashboard、步骤条、报告页
```

---

## 2. 前端技术选型

### 2.1 前端框架

```text
框架：React 18+
构建工具：Vite
语言：TypeScript
路由：React Router
状态管理：Zustand 或 Redux Toolkit，优先 Zustand
UI 组件库：Ant Design
HTTP 请求：Axios
Markdown 渲染：react-markdown
图表：ECharts / Recharts，优先 ECharts
文件上传：Ant Design Upload
表格展示：Ant Design Table
```

### 2.2 前端职责

React 前端负责：

```text
1. 用户登录 / 注册
2. 合同上传
3. 合同列表展示
4. 合同详情展示
5. MinerU 解析状态展示
6. Markdown 解析结果预览
7. 合同章节列表展示
8. 多 Agent 审查进度展示
9. Agent 输入输出日志展示
10. 风险项展示
11. 修改建议展示
12. 最终审查报告展示
13. 管理员后台展示
```

### 2.3 前端页面风格

整体风格建议：

```text
1. 企业级后台系统风格
2. 左侧菜单 + 顶部用户栏
3. 合同审查流程用 Steps 组件展示
4. 风险等级使用颜色标签
5. 报告页使用 Markdown 渲染
6. Agent 日志用 Drawer / Modal 展示
```

---

## 3. 后端技术选型

### 3.1 FastAPI 后端

```text
框架：FastAPI
ASGI 服务器：Uvicorn
ORM：SQLAlchemy 2.x
数据库迁移：Alembic
数据校验：Pydantic v2
鉴权：JWT + OAuth2PasswordBearer
密码加密：passlib[bcrypt]
文件上传：FastAPI UploadFile
异步任务：BackgroundTasks，后续可替换 Celery
LLM 调用：httpx
环境变量：python-dotenv / pydantic-settings
日志：logging / loguru
```

### 3.2 数据库选择

课程项目推荐使用：

```text
开发阶段：SQLite
正式演示：MySQL
```

如果时间紧，可以全程使用 SQLite。  
如果想体现系统工程性，使用 MySQL。

推荐写法：

```text
SQLAlchemy ORM + Alembic
```

这样后续切换 SQLite / MySQL 比较方便。

### 3.3 文件存储

第一版使用本地文件系统：

```text
storage/
├── uploads/          # 用户上传的原始合同
├── mineru_output/    # MinerU 输出结果
├── reports/          # 导出的报告文件
└── temp/             # 临时文件
```

后续可扩展为 MinIO，但 MVP 不需要。

---

## 4. 系统总体架构

### 4.1 逻辑架构

```text
┌───────────────────────────────┐
│          React 前端             │
│ 登录 / 上传 / 解析 / 审查 / 报告 │
└───────────────┬───────────────┘
                │ Axios REST API
┌───────────────▼───────────────┐
│          FastAPI 后端            │
│ 用户、合同、解析、Agent、报告管理 │
└───────┬───────────────┬───────┘
        │               │
┌───────▼───────┐ ┌─────▼─────────┐
│    MinerU      │ │    LLM API     │
│ 文档解析        │ │ 多 Agent 分析   │
└───────┬───────┘ └─────┬─────────┘
        │               │
┌───────▼───────────────▼───────┐
│      数据库 + 本地文件存储       │
│ MySQL/SQLite + storage/         │
└───────────────────────────────┘
```

### 4.2 模块架构

FastAPI 后端内部划分为：

```text
auth 模块
- 注册
- 登录
- JWT 鉴权
- 当前用户信息

users 模块
- 用户信息
- 管理员用户管理

contracts 模块
- 合同上传
- 合同列表
- 合同详情
- 合同删除

parser 模块
- MinerU 调用
- Markdown 读取
- content_list.json 读取
- 解析结果入库

normalizer 模块
- Markdown 清洗
- 章节识别
- 表格保留
- 合同结构标准化

agents 模块
- BaseAgent
- ContractProfileAgent
- ClauseExtractionAgent
- RiskDetectionAgent
- SuggestionAgent
- ConsistencyCheckAgent
- ReportGenerationAgent
- AgentOrchestrator

reviews 模块
- 审查任务创建
- 审查进度查询
- Agent 日志查询
- 审查结果查询

reports 模块
- 报告保存
- 报告查看
- 报告导出

admin 模块
- 用户管理
- 合同管理
- Agent 日志管理
- 系统统计
```

---

## 5. 推荐仓库结构

```text
contract-review-system/
├── CLAUDE.md
├── README.md
├── .gitignore
├── docker-compose.yml
├── docs/
│   ├── requirement.md
│   ├── design.md
│   ├── api.md
│   ├── database.md
│   ├── uml/
│   └── screenshots/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── request.ts
│   │   │   ├── auth.ts
│   │   │   ├── contracts.ts
│   │   │   ├── reviews.ts
│   │   │   ├── reports.ts
│   │   │   └── admin.ts
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── AgentStepBar.tsx
│   │   │   ├── RiskLevelTag.tsx
│   │   │   ├── MarkdownViewer.tsx
│   │   │   ├── AgentLogDrawer.tsx
│   │   │   └── ContractStatusTag.tsx
│   │   ├── layouts/
│   │   │   └── MainLayout.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ContractUploadPage.tsx
│   │   │   ├── ContractListPage.tsx
│   │   │   ├── ContractDetailPage.tsx
│   │   │   ├── ParseResultPage.tsx
│   │   │   ├── ReviewProgressPage.tsx
│   │   │   ├── RiskAnalysisPage.tsx
│   │   │   ├── SuggestionPage.tsx
│   │   │   ├── ReportPage.tsx
│   │   │   └── admin/
│   │   ├── router/
│   │   │   └── index.tsx
│   │   ├── store/
│   │   │   └── authStore.ts
│   │   ├── types/
│   │   └── utils/
│   └── public/
│
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── alembic.ini
│   ├── main.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   ├── response.py
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── contract.py
│   │   │   ├── parse_job.py
│   │   │   ├── document_parse_result.py
│   │   │   ├── review_task.py
│   │   │   ├── agent_execution_log.py
│   │   │   ├── contract_clause.py
│   │   │   ├── risk_item.py
│   │   │   ├── modify_suggestion.py
│   │   │   └── review_report.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── contract.py
│   │   │   ├── parse.py
│   │   │   ├── review.py
│   │   │   ├── agent.py
│   │   │   └── report.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── contracts.py
│   │   │       ├── parse.py
│   │   │       ├── reviews.py
│   │   │       ├── reports.py
│   │   │       └── admin.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── file_storage_service.py
│   │   │   ├── contract_service.py
│   │   │   ├── mineru_service.py
│   │   │   ├── document_normalizer.py
│   │   │   ├── review_service.py
│   │   │   └── report_service.py
│   │   ├── agents/
│   │   │   ├── base_agent.py
│   │   │   ├── llm_client.py
│   │   │   ├── orchestrator.py
│   │   │   ├── contract_profile_agent.py
│   │   │   ├── clause_extraction_agent.py
│   │   │   ├── risk_detection_agent.py
│   │   │   ├── suggestion_agent.py
│   │   │   ├── consistency_check_agent.py
│   │   │   └── report_generation_agent.py
│   │   ├── prompts/
│   │   │   ├── contract_profile_agent.txt
│   │   │   ├── clause_extraction_agent.txt
│   │   │   ├── risk_detection_agent.txt
│   │   │   ├── suggestion_agent.txt
│   │   │   ├── consistency_check_agent.txt
│   │   │   └── report_generation_agent.txt
│   │   └── utils/
│   │       ├── json_utils.py
│   │       ├── text_utils.py
│   │       └── time_utils.py
│   ├── alembic/
│   └── tests/
│
├── database/
│   ├── schema.sql
│   └── init_data.sql
│
└── storage/
    ├── uploads/
    ├── mineru_output/
    ├── reports/
    └── temp/
```

---

## 6. 核心业务流程

### 6.1 合同上传流程

```text
用户选择合同文件
→ React 调用 POST /api/v1/contracts/upload
→ FastAPI 校验文件类型和大小
→ FileStorageService 保存文件
→ ContractService 创建 contract 记录
→ 返回 contract_id
```

合同上传后：

```text
contract.status = UPLOADED
```

支持文件：

```text
.pdf
.docx
.txt
.png
.jpg
.jpeg
```

MVP 优先支持：

```text
PDF
DOCX
TXT
```

---

### 6.2 MinerU 解析流程

```text
用户点击“开始解析”
→ React 调用 POST /api/v1/contracts/{contract_id}/parse
→ FastAPI 创建 parse_job 记录
→ 调用 MinerUService
→ MinerU 生成 Markdown / JSON / layout 文件
→ DocumentNormalizer 生成标准合同结构
→ 保存 document_parse_result
→ contract.status = PARSED
```

解析任务状态：

```text
WAITING
RUNNING
SUCCESS
FAILED
```

合同状态：

```text
UPLOADED
PARSING
PARSED
REVIEWING
COMPLETED
FAILED
```

---

### 6.3 多 Agent 审查流程

```text
用户点击“开始审查”
→ React 调用 POST /api/v1/contracts/{contract_id}/review
→ FastAPI 创建 review_task
→ 读取 normalized_document
→ AgentOrchestrator 顺序执行多个 Agent
→ 每个 Agent 结果写入 agent_execution_log
→ 写入 contract_clause / risk_item / modify_suggestion / review_report
→ contract.status = COMPLETED
```

Agent 顺序：

```text
ContractProfileAgent
→ ClauseExtractionAgent
→ RiskDetectionAgent
→ SuggestionAgent
→ ConsistencyCheckAgent
→ ReportGenerationAgent
```

---

## 7. MinerU 集成设计

### 7.1 MinerU 的角色

MinerU 只做文档解析，不做合同审查。

MinerU 输入：

```text
PDF / DOCX / 图片
```

MinerU 输出：

```text
Markdown
content_list.json
middle.json
layout.pdf
图片目录
```

系统后续基于 Markdown 和 JSON 做标准化。

### 7.2 MinerUService

文件：

```text
backend/app/services/mineru_service.py
```

职责：

```text
1. 接收 input_path 和 output_dir
2. 创建输出目录
3. 拼接 MinerU 命令
4. 调用 subprocess.run
5. 检查输出文件
6. 返回 MinerUParseResult
```

伪代码：

```python
class MinerUService:
    def parse(self, input_path: str, output_dir: str) -> dict:
        command = [
            "mineru",
            "-p", input_path,
            "-o", output_dir,
            "-b", "pipeline"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return self.collect_outputs(output_dir)
```

### 7.3 输出文件收集

需要查找并保存：

```text
markdown_path
content_json_path
middle_json_path
layout_pdf_path
image_dir
raw_markdown
```

注意：

```text
1. 数据库只存路径，不存大文件本体
2. raw_markdown 可以存入数据库，方便预览和审查
3. layout.pdf 可以用于答辩展示解析效果
4. content_list.json 用于结构化标准化
```

---

## 8. 文档标准化模块

### 8.1 模块名称

```text
DocumentNormalizer
```

文件：

```text
backend/app/services/document_normalizer.py
```

### 8.2 输入

```text
markdown_path
content_json_path
```

### 8.3 输出

```json
{
  "contract_id": 1,
  "title": "房屋租赁合同",
  "full_text": "合同全文",
  "sections": [
    {
      "section_id": "S1",
      "title": "第一条 合同主体",
      "content": "甲方：张三...",
      "page": 1,
      "order": 1
    }
  ],
  "tables": [
    {
      "table_id": "T1",
      "html": "<table>...</table>",
      "page": 2,
      "caption": ""
    }
  ],
  "metadata": {
    "source_file": "xxx.pdf",
    "parse_engine": "mineru"
  }
}
```

### 8.4 标准化规则

#### 规则 1：标题识别

识别以下形式：

```text
第一条 ...
第二条 ...
第1条 ...
一、...
二、...
1. ...
1.1 ...
（一）...
```

#### 规则 2：段落合并

如果当前行不是标题，并且上一行不是标题，则合并为同一段落。

#### 规则 3：表格保留

如果 content_list.json 中包含 table：

```text
1. 保留 html
2. 记录 page
3. 记录 table_id
4. 不强行转纯文本
```

#### 规则 4：清理无效内容

清理：

```text
1. 多余空行
2. 页眉页脚
3. 页码
4. 重复标题
5. 无意义符号
```

#### 规则 5：保留来源

每个 section 必须保留：

```text
section_id
page
order
source_text
```

后续风险项必须能回溯原文。

---

## 9. 多 Agent 设计

### 9.1 Agent 总体原则

所有 Agent 必须：

```text
1. 职责单一
2. 输入输出结构化
3. 输出合法 JSON
4. 不直接操作数据库
5. 不直接处理文件
6. 由 AgentOrchestrator 调度
7. 执行结果由 ReviewService 保存
```

### 9.2 BaseAgent

文件：

```text
backend/app/agents/base_agent.py
```

职责：

```text
1. 加载 prompt 模板
2. 构造 prompt
3. 调用 LLM
4. 解析 JSON
5. 校验输出
6. 返回 dict
```

伪代码：

```python
class BaseAgent:
    name: str
    prompt_file: str

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def run(self, input_data: dict) -> dict:
        prompt = self.build_prompt(input_data)
        raw_output = await self.llm_client.chat(prompt)
        json_output = self.parse_json(raw_output)
        self.validate(json_output)
        return json_output
```

### 9.3 LLMClient

文件：

```text
backend/app/agents/llm_client.py
```

要求：

```text
1. 支持 OpenAI-compatible API
2. 支持本地模型服务，例如 Ollama / vLLM / LM Studio
3. API Base、API Key、Model 从 .env 读取
4. 设置 timeout
5. 失败时抛出明确异常
```

环境变量：

```env
LLM_API_BASE=http://localhost:11434/v1
LLM_API_KEY=EMPTY
LLM_MODEL=qwen2.5
LLM_TIMEOUT=120
```

### 9.4 AgentOrchestrator

文件：

```text
backend/app/agents/orchestrator.py
```

职责：

```text
1. 接收 normalized_document
2. 按顺序执行各 Agent
3. 收集中间结果
4. 返回完整审查结果
5. 不直接写数据库
```

伪代码：

```python
class AgentOrchestrator:
    async def run_review(self, normalized_document: dict) -> dict:
        profile = await self.profile_agent.run({
            "contract_document": normalized_document
        })

        clauses = await self.clause_agent.run({
            "contract_document": normalized_document,
            "contract_profile": profile
        })

        risks = await self.risk_agent.run({
            "contract_profile": profile,
            "clauses": clauses
        })

        suggestions = await self.suggestion_agent.run({
            "risks": risks,
            "clauses": clauses
        })

        check = await self.check_agent.run({
            "contract_document": normalized_document,
            "profile": profile,
            "clauses": clauses,
            "risks": risks,
            "suggestions": suggestions
        })

        report = await self.report_agent.run({
            "profile": profile,
            "clauses": clauses,
            "risks": risks,
            "suggestions": suggestions,
            "check": check
        })

        return {
            "profile": profile,
            "clauses": clauses,
            "risks": risks,
            "suggestions": suggestions,
            "consistency_check": check,
            "report": report
        }
```

---

## 10. 各 Agent 输出规范

### 10.1 ContractProfileAgent

职责：提取合同基本画像。

输出：

```json
{
  "contract_type": "房屋租赁合同",
  "party_a": "张三",
  "party_b": "李四",
  "sign_date": "2026-06-01",
  "amount": "3000元/月",
  "duration": "2026-06-01 至 2027-06-01",
  "subject": "房屋租赁",
  "summary": "本合同主要约定甲方将房屋出租给乙方，乙方按月支付租金。",
  "missing_fields": []
}
```

### 10.2 ClauseExtractionAgent

职责：抽取关键条款。

输出：

```json
{
  "clauses": [
    {
      "clause_id": "C1",
      "clause_type": "付款条款",
      "title": "租金及支付方式",
      "content": "乙方应于每月5日前支付租金3000元。",
      "source_section_id": "S3",
      "page": 2,
      "status": "found"
    }
  ],
  "missing_clause_types": [
    "争议解决"
  ]
}
```

必须抽取的条款类型：

```text
主体条款
标的条款
付款条款
履行条款
违约责任
解除条款
保密条款
争议解决
不可抗力
其他特殊条款
```

### 10.3 RiskDetectionAgent

职责：识别潜在风险。

输出：

```json
{
  "risks": [
    {
      "risk_id": "R1",
      "risk_level": "中风险",
      "risk_type": "违约责任不明确",
      "related_clause_id": "C5",
      "source_text": "任何一方违约，应承担相应责任。",
      "reason": "该条款未明确违约金计算方式、赔偿范围和责任承担方式。",
      "impact": "发生争议时可能难以确定赔偿标准。",
      "need_human_review": true
    }
  ],
  "overall_risk": "中风险"
}
```

风险等级：

```text
高风险
中风险
低风险
```

常见风险类型：

```text
主体信息缺失
金额不明确
付款时间不明确
违约责任模糊
解除条件不清楚
争议解决方式缺失
权利义务不对等
期限不明确
押金退还条件不明确
保密范围过宽
责任限制不合理
重要条款缺失
```

### 10.4 SuggestionAgent

职责：生成修改建议。

输出：

```json
{
  "suggestions": [
    {
      "suggestion_id": "SUG1",
      "risk_id": "R1",
      "original_text": "任何一方违约，应承担相应责任。",
      "suggested_text": "任何一方违反本合同约定并给对方造成损失的，应赔偿因此产生的直接损失；如逾期付款，每逾期一日按未付款金额的0.05%支付违约金。",
      "reason": "建议明确违约责任承担方式、赔偿范围和计算标准。",
      "rewrite_type": "明确化"
    }
  ]
}
```

### 10.5 ConsistencyCheckAgent

职责：检查前面 Agent 输出是否一致。

输出：

```json
{
  "passed": true,
  "issues": [
    {
      "issue_id": "I1",
      "issue_type": "风险依据不足",
      "description": "风险项 R2 提到付款时间不明确，但付款条款 C3 已写明每月5日前付款。",
      "target_agent": "RiskDetectionAgent",
      "target_id": "R2",
      "suggested_action": "建议人工复核或降低风险等级。"
    }
  ]
}
```

### 10.6 ReportGenerationAgent

职责：生成最终报告。

输出：

```json
{
  "report_title": "房屋租赁合同智能审查报告",
  "overall_risk": "中风险",
  "summary": "本合同主体和租金信息较明确，但违约责任和争议解决条款存在一定不完善之处。",
  "risk_statistics": {
    "high": 0,
    "medium": 2,
    "low": 3
  },
  "markdown_report": "# 合同审查报告\n\n...",
  "disclaimer": "本报告由 AI 系统自动生成，仅用于合同阅读辅助和风险提示，不构成正式法律意见。"
}
```

---

## 11. Prompt 规则

所有 Agent prompt 均放在：

```text
backend/app/prompts/
```

所有 Agent 必须要求 LLM：

```text
1. 只基于输入内容分析
2. 不要编造合同中不存在的内容
3. 无法确定的字段填 null
4. 输出必须是合法 JSON
5. 不要输出 Markdown 代码块
6. 不要输出解释性前缀
7. 不要直接下法律结论
8. 风险提示必须建议人工复核
```

JSON 解析失败处理：

```text
1. 尝试从文本中提取第一个 JSON 对象
2. 解析失败则重试一次
3. 重试时加入“上一次输出不是合法 JSON，请严格输出 JSON”
4. 仍失败则 Agent 状态置为 FAILED
```

---

## 12. 数据库设计

### 12.1 user 表

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(128),
    role VARCHAR(32) NOT NULL DEFAULT 'USER',
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

MySQL 可将 `AUTOINCREMENT` 改为 `AUTO_INCREMENT`。

### 12.2 contract 表

```sql
CREATE TABLE contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    stored_file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(32) NOT NULL,
    file_size INTEGER,
    contract_type VARCHAR(64),
    title VARCHAR(255),
    status VARCHAR(32) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### 12.3 parse_job 表

```sql
CREATE TABLE parse_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    input_path VARCHAR(500) NOT NULL,
    output_dir VARCHAR(500),
    backend VARCHAR(64) DEFAULT 'mineru',
    status VARCHAR(32) NOT NULL,
    error_message TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    created_at DATETIME NOT NULL
);
```

### 12.4 document_parse_result 表

```sql
CREATE TABLE document_parse_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    parse_job_id INTEGER NOT NULL,
    markdown_path VARCHAR(500),
    content_json_path VARCHAR(500),
    middle_json_path VARCHAR(500),
    layout_pdf_path VARCHAR(500),
    image_dir VARCHAR(500),
    raw_markdown TEXT,
    normalized_json TEXT,
    created_at DATETIME NOT NULL
);
```

### 12.5 review_task 表

```sql
CREATE TABLE review_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL,
    current_step VARCHAR(64),
    error_message TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    created_at DATETIME NOT NULL
);
```

### 12.6 agent_execution_log 表

```sql
CREATE TABLE agent_execution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    contract_id INTEGER NOT NULL,
    agent_name VARCHAR(128) NOT NULL,
    input_json TEXT,
    output_json TEXT,
    status VARCHAR(32) NOT NULL,
    error_message TEXT,
    started_at DATETIME,
    finished_at DATETIME,
    duration_ms INTEGER
);
```

### 12.7 contract_clause 表

```sql
CREATE TABLE contract_clause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    clause_id VARCHAR(64),
    clause_type VARCHAR(64),
    title VARCHAR(255),
    content TEXT,
    source_section_id VARCHAR(64),
    page_no INTEGER,
    status VARCHAR(32),
    created_at DATETIME NOT NULL
);
```

### 12.8 risk_item 表

```sql
CREATE TABLE risk_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    risk_id VARCHAR(64),
    risk_level VARCHAR(32),
    risk_type VARCHAR(128),
    related_clause_id VARCHAR(64),
    source_text TEXT,
    reason TEXT,
    impact TEXT,
    need_human_review BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL
);
```

### 12.9 modify_suggestion 表

```sql
CREATE TABLE modify_suggestion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    risk_id VARCHAR(64),
    suggestion_id VARCHAR(64),
    original_text TEXT,
    suggested_text TEXT,
    reason TEXT,
    rewrite_type VARCHAR(64),
    created_at DATETIME NOT NULL
);
```

### 12.10 review_report 表

```sql
CREATE TABLE review_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    title VARCHAR(255),
    overall_risk VARCHAR(32),
    summary TEXT,
    report_json TEXT,
    report_markdown TEXT,
    created_at DATETIME NOT NULL
);
```

---

## 13. 后端 API 设计

统一响应格式：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

错误响应：

```json
{
  "code": 500,
  "message": "错误信息",
  "data": null
}
```

### 13.1 认证接口

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### 13.2 合同接口

```http
POST   /api/v1/contracts/upload
GET    /api/v1/contracts
GET    /api/v1/contracts/{contract_id}
DELETE /api/v1/contracts/{contract_id}
```

### 13.3 解析接口

```http
POST /api/v1/contracts/{contract_id}/parse
GET  /api/v1/contracts/{contract_id}/parse-status
GET  /api/v1/contracts/{contract_id}/parse-result
```

### 13.4 审查接口

```http
POST /api/v1/contracts/{contract_id}/review
GET  /api/v1/review-tasks/{task_id}
GET  /api/v1/review-tasks/{task_id}/progress
GET  /api/v1/review-tasks/{task_id}/agent-logs
GET  /api/v1/review-tasks/{task_id}/profile
GET  /api/v1/review-tasks/{task_id}/clauses
GET  /api/v1/review-tasks/{task_id}/risks
GET  /api/v1/review-tasks/{task_id}/suggestions
```

### 13.5 报告接口

```http
GET /api/v1/reports/{task_id}
GET /api/v1/reports/{task_id}/export
```

### 13.6 管理员接口

```http
GET /api/v1/admin/users
GET /api/v1/admin/contracts
GET /api/v1/admin/review-tasks
GET /api/v1/admin/agent-logs
GET /api/v1/admin/statistics
```

---

## 14. React 页面设计

### 14.1 登录页

路径：

```text
/login
```

功能：

```text
1. 输入用户名和密码
2. 调用登录接口
3. 保存 token
4. 跳转 Dashboard
```

### 14.2 注册页

路径：

```text
/register
```

功能：

```text
1. 输入用户名、邮箱、密码
2. 调用注册接口
3. 注册成功后跳转登录
```

### 14.3 Dashboard

路径：

```text
/dashboard
```

展示：

```text
1. 已上传合同数量
2. 已完成审查数量
3. 高风险合同数量
4. 最近审查记录
5. 风险等级统计图
```

### 14.4 合同上传页

路径：

```text
/contracts/upload
```

功能：

```text
1. 上传 PDF / DOCX / TXT
2. 选择合同类型，可选
3. 上传成功后跳转合同详情
```

### 14.5 合同列表页

路径：

```text
/contracts
```

字段：

```text
合同名称
合同类型
上传时间
解析状态
审查状态
整体风险
操作
```

操作：

```text
查看详情
开始解析
开始审查
查看报告
删除
```

### 14.6 合同详情页

路径：

```text
/contracts/:id
```

展示：

```text
1. 合同基本信息
2. 原始文件信息
3. 当前状态
4. 解析按钮
5. 审查按钮
6. 解析结果入口
7. 审查结果入口
```

### 14.7 MinerU 解析结果页

路径：

```text
/contracts/:id/parse-result
```

展示：

```text
1. 解析状态
2. Markdown 预览
3. 标准化章节列表
4. 表格列表
5. layout.pdf 下载或预览
```

### 14.8 审查进度页

路径：

```text
/review-tasks/:taskId/progress
```

展示 Steps：

```text
合同画像 Agent
→ 条款抽取 Agent
→ 风险识别 Agent
→ 修改建议 Agent
→ 一致性校验 Agent
→ 报告生成 Agent
```

每个 Agent 展示：

```text
状态
开始时间
结束时间
耗时
查看输入
查看输出
错误信息
```

### 14.9 风险分析页

路径：

```text
/review-tasks/:taskId/risks
```

展示：

```text
1. 风险等级统计
2. 风险项列表
3. 风险对应原文
4. 风险原因
5. 可能影响
```

### 14.10 修改建议页

路径：

```text
/review-tasks/:taskId/suggestions
```

展示：

```text
1. 原条款
2. 风险说明
3. 建议修改文本
4. 修改理由
```

### 14.11 报告页

路径：

```text
/reports/:taskId
```

展示：

```text
1. 合同基本信息
2. 合同摘要
3. 风险总览
4. 风险明细
5. 修改建议
6. 一致性检查结果
7. 免责声明
8. 导出按钮
```

### 14.12 管理员后台

路径：

```text
/admin
```

功能：

```text
1. 用户管理
2. 合同管理
3. 审查任务管理
4. Agent 日志管理
5. 系统统计
```

---

## 15. 状态枚举

### 15.1 ContractStatus

```text
UPLOADED
PARSING
PARSED
REVIEWING
COMPLETED
FAILED
```

### 15.2 ParseJobStatus

```text
WAITING
RUNNING
SUCCESS
FAILED
```

### 15.3 ReviewTaskStatus

```text
WAITING
RUNNING
SUCCESS
FAILED
```

### 15.4 AgentStatus

```text
WAITING
RUNNING
SUCCESS
FAILED
```

### 15.5 RiskLevel

```text
HIGH
MEDIUM
LOW
```

前端显示：

```text
HIGH    → 高风险
MEDIUM  → 中风险
LOW     → 低风险
```

---

## 16. 后端配置

### 16.1 .env.example

```env
APP_NAME=Contract Review System
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000

DATABASE_URL=sqlite:///./contract_review.db
# MySQL 示例：
# DATABASE_URL=mysql+pymysql://root:root@localhost:3306/contract_review

JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

STORAGE_ROOT=./storage
UPLOAD_DIR=./storage/uploads
MINERU_OUTPUT_DIR=./storage/mineru_output
REPORT_DIR=./storage/reports

LLM_API_BASE=http://localhost:11434/v1
LLM_API_KEY=EMPTY
LLM_MODEL=qwen2.5
LLM_TIMEOUT=120

MINERU_BACKEND=pipeline
MINERU_TIMEOUT=600

CORS_ORIGINS=http://localhost:5173
```

### 16.2 requirements.txt

```text
fastapi
uvicorn[standard]
sqlalchemy
alembic
pydantic
pydantic-settings
python-multipart
python-jose[cryptography]
passlib[bcrypt]
httpx
python-dotenv
pymysql
loguru
aiofiles
```

MinerU 依赖根据部署环境单独安装，不强行写入基础 requirements。

---

## 17. 错误处理设计

### 17.1 文件上传错误

情况：

```text
1. 文件为空
2. 文件过大
3. 文件类型不支持
4. 保存失败
```

处理：

```json
{
  "code": 400,
  "message": "文件类型不支持",
  "data": null
}
```

### 17.2 MinerU 解析错误

情况：

```text
1. MinerU 命令执行失败
2. 解析超时
3. 输出文件缺失
4. Markdown 为空
```

处理：

```text
1. parse_job.status = FAILED
2. contract.status = FAILED
3. 保存 error_message
4. 前端显示失败原因
```

### 17.3 Agent 执行错误

情况：

```text
1. LLM API 超时
2. LLM 输出不是 JSON
3. JSON schema 不符合要求
4. 某个 Agent 执行失败
```

处理：

```text
1. agent_execution_log.status = FAILED
2. review_task.status = FAILED
3. 保存失败 Agent 名称和错误原因
4. 前端允许重新发起审查
```

---

## 18. 安全设计

### 18.1 用户权限

```text
1. 普通用户只能查看自己的合同
2. 管理员可以查看所有合同和任务
3. 所有业务接口默认需要 JWT
4. 登录注册接口除外
```

### 18.2 文件安全

```text
1. 校验文件后缀
2. 限制文件大小
3. 文件名使用 UUID 重命名
4. 不直接暴露服务器真实路径
5. 下载文件时通过后端接口读取
```

### 18.3 AI 安全

```text
1. Prompt 中要求只基于合同内容分析
2. 报告中加入免责声明
3. 不输出确定性法律结论
4. 对高风险建议人工复核
```

---

## 19. MVP 实现顺序

严格按以下顺序开发。

### 阶段 1：项目骨架

```text
1. 创建 monorepo
2. 创建 React + Vite + TypeScript 前端
3. 创建 FastAPI 后端
4. 配置数据库连接
5. 配置 CORS
6. 配置统一响应格式
7. 完成前后端联通测试
```

验收标准：

```text
前端能请求 FastAPI
FastAPI 能连接数据库
```

### 阶段 2：用户与鉴权

```text
1. user 模型
2. 注册接口
3. 登录接口
4. JWT 生成与校验
5. 前端登录注册页
6. 路由守卫
```

验收标准：

```text
用户可以注册、登录，登录后访问合同页面。
```

### 阶段 3：合同上传与管理

```text
1. contract 模型
2. 文件保存服务
3. 上传接口
4. 合同列表接口
5. 合同详情接口
6. 前端上传页、列表页、详情页
```

验收标准：

```text
用户可以上传合同，合同文件保存到 storage/uploads，数据库有记录。
```

### 阶段 4：MinerU 解析

```text
1. parse_job 模型
2. document_parse_result 模型
3. MinerUService
4. 解析接口
5. 解析状态接口
6. 前端解析按钮和解析状态展示
```

验收标准：

```text
上传 PDF 后可以调用 MinerU 得到 Markdown，并在前端预览。
```

### 阶段 5：文档标准化

```text
1. DocumentNormalizer
2. Markdown 清洗
3. 章节识别
4. normalized_json 保存
5. 前端章节列表展示
```

验收标准：

```text
合同可以被切分为 sections，每个 section 有 title、content、order。
```

### 阶段 6：第一个 Agent

```text
1. LLMClient
2. BaseAgent
3. ContractProfileAgent
4. agent_execution_log 模型
5. 前端展示合同画像
```

验收标准：

```text
系统能提取合同类型、甲方、乙方、金额、期限、摘要。
```

### 阶段 7：完整多 Agent 工作流

```text
1. ClauseExtractionAgent
2. RiskDetectionAgent
3. SuggestionAgent
4. ConsistencyCheckAgent
5. ReportGenerationAgent
6. AgentOrchestrator
7. ReviewService 保存结果
```

验收标准：

```text
系统可以从合同解析结果生成完整审查报告，每个 Agent 都有执行日志。
```

### 阶段 8：前端结果页面

```text
1. 审查进度页
2. Agent 日志 Drawer
3. 风险分析页
4. 修改建议页
5. 报告页
```

验收标准：

```text
答辩时可以完整演示：
上传 → 解析 → 审查 → 风险 → 建议 → 报告
```

### 阶段 9：管理员后台和项目文档

```text
1. 用户管理
2. 合同管理
3. 审查任务管理
4. Agent 日志管理
5. 统计页面
6. UML 图
7. 需求文档、设计文档、项目管理文档
```

---

## 20. 不建议第一版实现的功能

```text
1. 在线编辑 Word
2. 真实法律法规检索
3. 复杂 RAG 法条库
4. 多用户实时协同编辑
5. 支付系统
6. 手机 App 原生端
7. 复杂工作流回滚
8. 多模型投票
9. 自动替用户签合同
10. 企业微信 / 钉钉集成
```

---

## 21. 课程文档对应关系

### 21.1 需求文档

重点写：

```text
1. 合同审查场景的问题
2. 目标用户
3. 竞品分析
4. 功能分解树
5. 用例图
6. 原型图和页面说明
7. 开发计划
8. 领域模型类图
9. 包图
10. 活动图 / 顺序图
```

### 21.2 设计文档

重点写：

```text
1. 技术选型：React + FastAPI + MinerU + LLM
2. 前后端分离架构
3. MinerU 文档解析方案
4. 多 Agent 协作方案
5. 数据库设计
6. 接口设计
7. JWT 鉴权设计
8. 文件存储设计
9. 错误处理
10. 部署方案
```

### 21.3 项目管理文档

重点写：

```text
1. 个人独立开发
2. AI 工具使用情况
3. 开发记录
4. Git commit 记录
5. 问题与解决方案
6. 项目总结
```

---

## 22. UML 图建议

### 22.1 用例图角色

```text
普通用户
管理员
MinerU 解析服务
LLM Agent 服务
```

普通用户用例：

```text
注册登录
上传合同
发起解析
查看解析结果
发起审查
查看风险分析
查看修改建议
导出审查报告
管理历史合同
```

管理员用例：

```text
管理用户
管理合同
查看审查任务
查看 Agent 日志
查看系统统计
```

### 22.2 核心类图

类：

```text
User
Contract
ParseJob
DocumentParseResult
ReviewTask
AgentExecutionLog
ContractClause
RiskItem
ModifySuggestion
ReviewReport
FileStorageService
MinerUService
DocumentNormalizer
BaseAgent
ContractProfileAgent
ClauseExtractionAgent
RiskDetectionAgent
SuggestionAgent
ConsistencyCheckAgent
ReportGenerationAgent
AgentOrchestrator
ReviewService
ReportService
```

关系：

```text
User 1 --- * Contract
Contract 1 --- * ParseJob
Contract 1 --- 1 DocumentParseResult
Contract 1 --- * ReviewTask
ReviewTask 1 --- * AgentExecutionLog
ReviewTask 1 --- * ContractClause
ContractClause 1 --- * RiskItem
RiskItem 1 --- * ModifySuggestion
ReviewTask 1 --- 1 ReviewReport
BaseAgent <|-- ContractProfileAgent
BaseAgent <|-- ClauseExtractionAgent
BaseAgent <|-- RiskDetectionAgent
BaseAgent <|-- SuggestionAgent
BaseAgent <|-- ConsistencyCheckAgent
BaseAgent <|-- ReportGenerationAgent
AgentOrchestrator o-- BaseAgent
ReviewService --> AgentOrchestrator
ReviewService --> ReportService
```

### 22.3 顺序图

发起审查顺序：

```text
用户
→ React 前端
→ FastAPI Contract API
→ ReviewService
→ 读取 DocumentParseResult
→ AgentOrchestrator
→ ContractProfileAgent
→ ClauseExtractionAgent
→ RiskDetectionAgent
→ SuggestionAgent
→ ConsistencyCheckAgent
→ ReportGenerationAgent
→ ReviewService 保存结果
→ React 前端展示报告
```

---

## 23. AI 编程助手实现规则

后续让 AI 写代码时必须遵守：

```text
1. 不要一次性生成整个项目。
2. 每次只实现一个模块。
3. 每个模块完成后说明新增文件、修改文件和测试方式。
4. 后端接口必须和本文档保持一致。
5. 数据库字段必须和本文档保持一致，除非明确说明修改原因。
6. Agent 输出必须是 JSON。
7. 不要把所有逻辑写在 API 路由函数中。
8. LLM 调用必须封装在 LLMClient。
9. MinerU 调用必须封装在 MinerUService。
10. 文件路径不要硬编码，必须放在配置文件中。
11. 所有异常必须返回统一响应结构。
12. 所有用户数据必须按 user_id 隔离。
13. 报告必须包含免责声明。
14. React 组件不要写得过大，页面和通用组件要拆分。
15. API 请求必须统一封装在 frontend/src/api/。
```

---

## 24. 答辩演示脚本

演示流程：

```text
1. 登录系统
2. 上传一份房屋租赁合同 PDF
3. 点击开始解析
4. 展示 MinerU 解析出的 Markdown
5. 展示合同章节切分结果
6. 点击开始智能审查
7. 展示多 Agent 执行步骤条
8. 打开 Agent 日志，说明每个 Agent 有独立输入输出
9. 展示风险分析结果
10. 展示修改建议
11. 展示最终审查报告
12. 展示管理员后台中的审查任务和 Agent 日志
```

答辩重点表述：

```text
本系统不是简单调用一次大语言模型，而是先通过 MinerU 将合同文件解析为 Markdown 和结构化 JSON，再通过多 Agent 工作流分阶段完成合同画像、条款抽取、风险识别、修改建议、一致性校验和报告生成。每个 Agent 的输入输出都会持久化保存，因此系统具有较好的可追踪性、可解释性和工程完整性。
```

---

## 25. 最终交付内容

需要提交：

```text
1. frontend React 前端源码
2. backend FastAPI 后端源码
3. database 数据库脚本
4. README.md
5. CLAUDE.md / PROJECT_SPEC.md
6. 需求文档
7. 设计文档
8. 项目管理文档
9. 系统运行截图
10. UML 图
11. Git commit 记录截图或导出
```

---

## 26. 最终范围确认

最终版本至少完成：

```text
1. 用户注册登录
2. 合同上传
3. MinerU 解析
4. Markdown 预览
5. 合同章节标准化
6. 多 Agent 审查
7. Agent 执行日志
8. 风险分析
9. 修改建议
10. 报告生成
11. 合同历史记录
12. 管理员查看任务与日志
```

有余力再完成：

```text
1. 报告 PDF 导出
2. 合同类型管理
3. 风险规则管理
4. 统计图表
5. layout.pdf 预览
```

不要为了扩展功能牺牲主流程。  
主流程必须稳定跑通：

```text
上传合同 → MinerU 解析 → 多 Agent 审查 → 生成报告
```
