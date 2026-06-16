# ClauseMind

ClauseMind 是一个基于 **React + FastAPI + MinerU + OpenAI-compatible LLM + 多 Agent** 的合同智能审查系统。系统支持合同上传、MinerU 文档解析、结构化标准化、六阶段 Agent 审查、风险识别、修改建议、报告导出和管理员后台，适合作为课程设计、AI 工程实践或合同辅助审查原型。

> 本系统用于合同阅读辅助和风险提示，不构成正式法律意见。重要合同请咨询专业律师或法律顾问。

## 功能概览

- 用户注册、登录、JWT 鉴权和管理员权限控制
- 合同文件上传、列表、详情、删除和用户数据隔离
- MinerU 解析接入，支持 `hybrid-auto-engine` 配置
- 解析结果 Markdown 预览和结构化标准化
- 六阶段多 Agent 审查流程：
  - ContractProfileAgent：合同画像
  - ClauseExtractionAgent：条款抽取
  - RiskDetectionAgent：风险识别
  - SuggestionAgent：修改建议
  - ConsistencyCheckAgent：一致性校验
  - ReportGenerationAgent：报告生成
- Agent 执行日志持久化，可查看输入、输出、错误和耗时
- 风险分析、修改建议、审查报告页面
- 报告 Markdown / HTML 导出
- 管理员后台：用户、合同、审查任务、Agent 日志、系统统计
- 课程交付文档和 Mermaid UML 图
- Demo seed 脚本，一键生成演示账号和完整审查数据

## 技术栈

| Layer | Stack |
| --- | --- |
| Frontend | React 18, Vite, TypeScript, Ant Design, Axios, Zustand |
| Backend | FastAPI, SQLAlchemy 2.x, Alembic, Pydantic Settings, httpx |
| Python Env | uv |
| Database | SQLite 默认，保留 MySQL-compatible URL 配置 |
| Document Parse | MinerU CLI |
| LLM | OpenAI-compatible Chat Completions API |
| Storage | Local `storage/` directories |

## 目录结构

```text
ClauseMind/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/          # LLMClient, BaseAgent, six review agents
│   │   ├── api/v1/          # auth/contracts/parse/review/report/admin APIs
│   │   ├── core/            # config, db, response, security, exceptions
│   │   ├── models/          # SQLAlchemy models
│   │   ├── prompts/         # Agent prompt templates
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # MinerU, normalizer, review orchestration
│   ├── migrations/          # Alembic migrations
│   ├── scripts/seed_demo.py # Demo data seeder
│   └── tests/               # Backend tests
├── frontend/                # React + Vite frontend
├── docs/                    # Requirement/design/API/database/UML docs
├── storage/                 # Ignored local uploads, outputs, reports
└── third_party/MinerU       # Vendored MinerU source for inspection/integration
```

## 环境约束

MinerU 可以来自系统 PATH、独立 conda/uv 环境，或外部已有环境中的 CLI。请遵守：

- 不要在 ClauseMind 启动过程中修改外部 MinerU 源码目录或 conda 环境。
- 不要为了本项目往已有 MinerU 环境里安装或升级包；需要改依赖时新建独立环境。
- ClauseMind 代码中如需查看 MinerU 源码，优先使用本仓库的 `third_party/MinerU`。
- 本地真实密钥和机器相关路径只放在 `backend/.env`，不要提交。

## 后端启动

```bash
cd backend
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

后端默认地址：

```text
http://localhost:8000
```

常用入口：

- API docs: `http://localhost:8000/docs`
- Health: `GET /health`
- Public config: `GET /api/v1/system/config`

## 后端环境变量

参考 `backend/.env.example`：

```env
DATABASE_URL=sqlite:///./contract_review.db
JWT_SECRET_KEY=change-this-secret

LLM_API_BASE=https://api.example.com/
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=gemini-3-flash-preview
LLM_TIMEOUT=120

MINERU_COMMAND=mineru
MINERU_BACKEND=hybrid-auto-engine
MINERU_TIMEOUT=600
# MINERU_CUDA_VISIBLE_DEVICES=2

CORS_ORIGINS=http://localhost:5173
```

生产或演示环境请替换 `JWT_SECRET_KEY` 和 LLM 配置。不要把真实 `LLM_API_KEY` 写入 README、docs 或 git。

### MinerU 配置方式

如果 `mineru` 已在当前 shell 的 PATH 中，保持默认即可：

```env
MINERU_COMMAND=mineru
```

如果 MinerU 在外部环境里，请在本机 `backend/.env` 写你的实际 CLI 路径，例如：

```env
MINERU_COMMAND=<path-to-mineru-env>/bin/mineru
```

多 GPU 机器上，如果 `hybrid-auto-engine` 默认占用的 GPU 显存不足，可以只给 MinerU 子进程指定 GPU：

```env
MINERU_CUDA_VISIBLE_DEVICES=2
```

这个变量只影响 ClauseMind 调起 MinerU 的子进程，不会修改外部环境。

### LLM 配置方式

后端通过 OpenAI-compatible Chat Completions 接口调用模型：

```env
LLM_API_BASE=https://your-openai-compatible-api.example.com/
LLM_API_KEY=replace-with-your-api-key
LLM_MODEL=gemini-3-flash-preview
LLM_TIMEOUT=120
```

`LLM_API_BASE` 可以填服务根地址，也可以填已经包含 `/v1` 的地址；后端会在客户端里统一处理 Chat Completions endpoint。`GET /api/v1/system/config` 只暴露是否已配置，不会返回 API key。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端默认地址：

```text
http://localhost:5173
```

Vite 会将 `/api` 和 `/health` 请求代理到后端。

## Demo 数据

可以用 seed 脚本快速生成管理员、普通用户、合同、解析结果、标准化结果、审查任务、Agent 日志、风险、建议和报告。

```bash
cd backend
uv run python scripts/seed_demo.py
```

脚本是幂等的，重复执行不会创建大量重复用户或演示合同。

演示账号：

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123456` |
| User | `demo` | `demo123456` |

## 业务演示流程

1. 启动后端和前端。
2. 执行 `uv run python scripts/seed_demo.py`。
3. 登录普通用户 `demo / demo123456`。
4. 进入合同详情，查看解析结果、审查进度、风险分析、修改建议和审查报告。
5. 在报告页导出 Markdown 或 HTML。
6. 登录管理员 `admin / admin123456`。
7. 进入管理员后台，查看用户、合同、审查任务、Agent 日志和系统统计。

也可以不使用 demo 数据，按真实流程操作：

```text
注册/登录
→ 上传合同
→ 开始 MinerU 解析
→ 生成结构化结果
→ 开始多 Agent 审查
→ 查看风险/建议/报告
→ 导出报告
→ 管理员后台审计
```

## 主要 API

| Module | Examples |
| --- | --- |
| Auth | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me` |
| Contracts | `POST /api/v1/contracts/upload`, `GET /api/v1/contracts`, `GET /api/v1/contracts/{id}` |
| Parse | `POST /api/v1/contracts/{id}/parse`, `GET /api/v1/contracts/{id}/parse-result`, `POST /api/v1/contracts/{id}/normalize` |
| Review | `POST /api/v1/contracts/{id}/review`, `GET /api/v1/review-tasks/{task_id}/progress` |
| Results | `GET /api/v1/review-tasks/{task_id}/risks`, `/suggestions`, `/profile` |
| Reports | `GET /api/v1/reports/{task_id}`, `/export`, `/export/html` |
| Admin | `GET /api/v1/admin/users`, `/contracts`, `/review-tasks`, `/agent-logs`, `/statistics` |

完整接口说明见 [docs/api.md](docs/api.md)。

## 文档

- [需求说明](docs/requirement.md)
- [系统设计](docs/design.md)
- [API 文档](docs/api.md)
- [数据库说明](docs/database.md)
- [UML / Mermaid 图](docs/uml.md)

## 测试与验证

后端：

```bash
cd backend
uv run pytest -q
uv run python -m compileall .
```

Fresh Alembic：

```bash
cd backend
rm -f clausemind-check.db
DATABASE_URL=sqlite:///./clausemind-check.db uv run alembic upgrade head
DATABASE_URL=sqlite:///./clausemind-check.db uv run alembic current --verbose
```

前端：

```bash
cd frontend
npm run build
```

Secret 检查示例：

```bash
git grep -n "LLM_API_KEY=" -- \
  ':!backend/.env' \
  ':!backend/.env.example' \
  ':!frontend/node_modules' \
  ':!backend/.venv' \
  ':!frontend/dist' || true
```

代码行数统计（排除 MinerU 和依赖/产物）：

```bash
cloc . \
  --exclude-dir=.git,.venv,node_modules,dist,__pycache__,.pytest_cache,third_party,storage,database \
  --not-match-f='.*\.pyc$|.*\.db$|.*\.sqlite$|.*\.sqlite3$|.*\.log$|.*package-lock\.json$'
```

## 安全说明

- `backend/.env` 不应提交。
- SQLite DB、上传文件、MinerU 输出、报告文件和缓存不应提交。
- 普通用户只能访问自己的合同、审查任务、日志和报告。
- Admin API 使用 `role == "admin"` 限制。
- LLM 调用统一封装在 `backend/app/agents/llm_client.py`。
- MinerU 调用统一封装在 `backend/app/services/mineru_service.py`。
- 报告必须保留 AI 免责声明。

## 当前状态

当前版本已完成从上传到审查报告的端到端主流程，并具备课程交付所需的后台、文档、测试和演示数据。后续可继续增强：

- Admin 分页体验和图表统计
- 报告 PDF 导出
- Agent 输出质量评估
- 异步任务队列
- 更严格的权限审计和操作日志
- 更丰富的合同类型规则
